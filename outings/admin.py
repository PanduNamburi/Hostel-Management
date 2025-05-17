from django.contrib import admin
from .models import Outing
from fees.models import Notification

@admin.register(Outing)
class OutingAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'destination', 'purpose', 'start_time', 'end_time',
        'status', 'approved_by', 'actual_return_time'
    )
    list_filter = ('status', 'start_time', 'end_time')
    search_fields = ('student__username', 'destination', 'purpose')
    ordering = ('-start_time',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_time'

    # Optional: Add bulk actions for admin
    actions = ['mark_as_approved', 'mark_as_rejected']

    def mark_as_approved(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} outing(s) marked as approved.")
    mark_as_approved.short_description = "Mark selected outings as approved"

    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} outing(s) marked as rejected.")
    mark_as_rejected.short_description = "Mark selected outings as rejected"

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            # Create notification based on status change
            if obj.status == 'approved':
                Notification.objects.create(
                    notification_type=Notification.OUTING_APPROVED,
                    outing=obj,
                    message=f"Your outing for {obj.start_time} to {obj.end_time} has been approved by {request.user.get_full_name()}"
                )
            elif obj.status == 'rejected':
                Notification.objects.create(
                    notification_type=Notification.OUTING_REJECTED,
                    outing=obj,
                    message=f"Your outing for {obj.start_time} to {obj.end_time} has been rejected by {request.user.get_full_name()}"
                )
        elif not change:  # New outing
            Notification.objects.create(
                notification_type=Notification.OUTING_REQUESTED,
                outing=obj,
                message=f"New outing request from {obj.student.get_full_name()} for {obj.start_time} to {obj.end_time}"
            )
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        # If user is admin, show all outings
        if request.user.is_superuser:
            return super().get_queryset(request)
        # If user is warden, show all outings
        elif request.user.groups.filter(name='Warden').exists():
            return super().get_queryset(request)
        # For students, show only their outings
        return super().get_queryset(request).filter(student=request.user)
