from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import FeeRecord, FeePayment, PaymentDetails, Notification
from .forms import FeeRecordForm
from django.db import models
from django.core.mail import send_mail
from django.conf import settings

def is_warden(user):
    return user.is_authenticated and user.role == 'warden'

@login_required
@user_passes_test(is_warden)
def fee_list(request):
    fees = FeeRecord.objects.all()
    student = request.GET.get('student')
    status = request.GET.get('status')
    due_date = request.GET.get('due_date')
    if student:
        fees = fees.filter(student__username__icontains=student)
    if status:
        fees = fees.filter(status=status)
    if due_date:
        fees = fees.filter(due_date=due_date)
    return render(request, 'fees/fee_list.html', {'fees': fees})

@login_required
@user_passes_test(is_warden)
def fee_update(request, pk):
    fee = get_object_or_404(FeeRecord, pk=pk)
    if request.method == 'POST':
        form = FeeRecordForm(request.POST, instance=fee)
        if form.is_valid():
            form.save()
            return redirect('fees:fee_list')
    else:
        form = FeeRecordForm(instance=fee)
    return render(request, 'fees/fee_form.html', {'form': form})

@login_required
def student_fee_status(request):
    fees = FeeRecord.objects.filter(student=request.user)
    payments = FeePayment.objects.filter(fee_record__student=request.user).order_by('-payment_date')
    total_fee = fees.aggregate(total=models.Sum('fee_amount'))['total'] or 0
    total_paid = FeePayment.objects.filter(fee_record__student=request.user, status='approved').aggregate(total=models.Sum('amount'))['total'] or 0
    total_due = total_fee - total_paid
    return render(request, 'fees/student_fee_status.html', {
        'fees': fees,
        'payments': payments,
        'total_fee': total_fee,
        'total_paid': total_paid,
        'total_due': total_due,
    })

@login_required
@user_passes_test(is_warden)
def fee_dashboard(request):
    total_collected = FeeRecord.objects.filter(status='paid').aggregate(total=models.Sum('fee_amount'))['total'] or 0
    total_pending = FeeRecord.objects.filter(status='unpaid').aggregate(total=models.Sum('fee_amount'))['total'] or 0
    return render(request, 'fees/fee_dashboard.html', {
        'total_collected': total_collected,
        'total_pending': total_pending,
    })

@login_required
def make_payment(request):
    payment_details = PaymentDetails.objects.last()
    message = None
    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        transaction_id = request.POST.get('transaction_id', '')
        payment_proof = request.FILES.get('payment_proof')
        fee_record = FeeRecord.objects.filter(student=request.user, status='unpaid').order_by('due_date').first()
        if fee_record:
            payment = FeePayment.objects.create(
                fee_record=fee_record,
                amount=amount,
                transaction_id=transaction_id,
                payment_proof=payment_proof,
                status='pending'
            )
            Notification.objects.create(
                notification_type=Notification.PAYMENT_RECEIVED,
                payment=payment,
                message=f"New payment of ₹{amount:.2f} received from {request.user.get_full_name() or request.user.username} (Transaction ID: {transaction_id})"
            )
            # Do NOT update due or status yet!
            # Optionally, notify admin here
            message = "Payment submitted for verification. Admin will review your payment soon."
        else:
            message = "No unpaid fee record found."
    return render(request, 'fees/make_payment.html', {'payment_details': payment_details, 'message': message})
