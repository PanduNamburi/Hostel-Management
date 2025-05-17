from django.contrib import admin
from .models import FeeRecord, FeePayment, PaymentDetails, Notification
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import format_html
from django.db import models

class FeePaymentInline(admin.TabularInline):
    model = FeePayment
    extra = 1

@admin.register(FeeRecord)
class FeeRecordAdmin(admin.ModelAdmin):
    inlines = [FeePaymentInline]
    list_display = ('student_name', 'fee_amount', 'total_paid', 'remaining_due', 'room_number')
    search_fields = (
        'student__username',
        'student__first_name',
        'student__last_name',
        'student__profile__room__room_number'
    )
    list_filter = ('status', 'due_date')
    readonly_fields = ('total_paid', 'remaining_due')

    def student_name(self, obj):
        return f"{obj.student.get_full_name()} ({obj.student.username})"
    student_name.short_description = "Student Name"
    student_name.admin_order_field = 'student__username'

    def room_number(self, obj):
        try:
            return obj.student.profile.room.room_number if obj.student.profile and obj.student.profile.room else "-"
        except:
            return "-"
    room_number.short_description = "Room Number"
    room_number.admin_order_field = 'student__profile__room__room_number'

    def total_paid(self, obj):
        total = obj.payments.filter(status='approved').aggregate(total=models.Sum('amount'))['total'] or 0
        return f"₹{total:.2f}"
    total_paid.short_description = "Total Paid"

    def remaining_due(self, obj):
        total_paid = obj.payments.filter(status='approved').aggregate(total=models.Sum('amount'))['total'] or 0
        due = max(obj.fee_amount - total_paid, 0)
        return f"₹{due:.2f}"
    remaining_due.short_description = "Remaining Due"

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'message', 'is_read', 'created_at', 'payment_link', 'outing_link')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('message', 'payment__transaction_id', 'outing__student__username')
    readonly_fields = ('notification_type', 'message', 'payment', 'outing', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 20

    def payment_link(self, obj):
        if obj.payment:
            return format_html('<a href="{}">{}</a>', 
                             f'/admin/fees/feepayment/{obj.payment.id}/change/',
                             obj.payment.transaction_id)
        return "-"
    payment_link.short_description = "Payment"

    def outing_link(self, obj):
        if obj.outing:
            return format_html('<a href="{}">{}</a>', 
                             f'/admin/outings/outingrequest/{obj.outing.id}/change/',
                             f"Outing Request #{obj.outing.id}")
        return "-"
    outing_link.short_description = "Outing Request"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected notifications as read"

    actions = ['mark_as_read']

    def get_queryset(self, request):
        # If user is admin, show all notifications
        if request.user.is_superuser:
            return super().get_queryset(request)
        # If user is warden, show only outing notifications
        elif request.user.groups.filter(name='Warden').exists():
            return super().get_queryset(request).filter(
                notification_type__in=[
                    Notification.OUTING_REQUESTED,
                    Notification.OUTING_APPROVED,
                    Notification.OUTING_REJECTED
                ]
            )
        # For other users, show only their notifications
        return super().get_queryset(request).filter(
            payment__fee_record__student=request.user
        )

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'amount', 'transaction_id', 'status', 'payment_date', 'payment_proof_tag', 'room_number')
    list_filter = ('status', 'payment_date')
    search_fields = (
        'fee_record__student__username',
        'fee_record__student__first_name',
        'fee_record__student__last_name',
        'transaction_id',
        'fee_record__student__profile__room__room_number'
    )
    readonly_fields = ('payment_proof_tag',)
    date_hierarchy = 'payment_date'
    list_per_page = 20

    def student_name(self, obj):
        student = obj.fee_record.student
        return f"{student.get_full_name()} ({student.username})"
    student_name.short_description = "Student Name"
    student_name.admin_order_field = 'fee_record__student__username'

    def room_number(self, obj):
        try:
            return obj.fee_record.student.profile.room.room_number if obj.fee_record.student.profile and obj.fee_record.student.profile.room else "-"
        except:
            return "-"
    room_number.short_description = "Room Number"
    room_number.admin_order_field = 'fee_record__student__profile__room__room_number'

    def payment_proof_tag(self, obj):
        if obj.payment_proof:
            return format_html('<img src="{}" width="100" />', obj.payment_proof.url)
        return "-"
    payment_proof_tag.short_description = "Payment Proof"

    def save_model(self, request, obj, form, change):
        # Create notification for new payment
        if not change:  # New payment
            Notification.objects.create(
                notification_type=Notification.PAYMENT_RECEIVED,
                payment=obj,
                message=f"New payment of ₹{obj.amount:.2f} received from {obj.fee_record.student.get_full_name()} (Transaction ID: {obj.transaction_id})"
            )
        
        # If status changed to approved, send confirmation email and create notification
        if 'status' in form.changed_data and obj.status == 'approved':
            student = obj.fee_record.student
            total_paid = obj.fee_record.payments.filter(status='approved').aggregate(total=models.Sum('amount'))['total'] or 0
            due = max(obj.fee_record.fee_amount - total_paid, 0)
            
            # Create notification
            Notification.objects.create(
                notification_type=Notification.PAYMENT_APPROVED,
                payment=obj,
                message=f"Payment of ₹{obj.amount:.2f} approved for {student.get_full_name()} (Transaction ID: {obj.transaction_id})"
            )
            
            # Send email
            print("Attempting to send payment approval email to:", student.email)
            send_mail(
                subject='Hostel Fee Payment Approved',
                message=(
                    f"Dear {student.get_full_name() or student.username},\n\n"
                    f"Your payment of ₹{obj.amount:.2f} (Transaction ID: {obj.transaction_id}) has been approved.\n"
                    f"Total Fee: ₹{obj.fee_record.fee_amount:.2f}\n"
                    f"Total Paid: ₹{total_paid:.2f}\n"
                    f"Remaining Due: ₹{due:.2f}\n\n"
                    "Thank you!"
                ),
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@hostel.com'),
                recipient_list=[student.email],
                fail_silently=False,
            )
        
        # If status changed to rejected, create notification
        elif 'status' in form.changed_data and obj.status == 'rejected':
            Notification.objects.create(
                notification_type=Notification.PAYMENT_REJECTED,
                payment=obj,
                message=f"Payment of ₹{obj.amount:.2f} rejected for {obj.fee_record.student.get_full_name()} (Transaction ID: {obj.transaction_id})"
            )
            
        super().save_model(request, obj, form, change)

@admin.register(PaymentDetails)
class PaymentDetailsAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'ifsc_code', 'upi_id')
