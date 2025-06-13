from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from accounts.models import CustomUser

class FeeRecord(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fee_records')
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    payment_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.student.get_full_name() or self.student.username} - {self.fee_amount} - {self.status}"

    def amount_paid(self):
        return sum(payment.amount for payment in self.payments.all())

    def is_fully_paid(self):
        return self.amount_paid() >= self.fee_amount

class FeePayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    fee_record = models.ForeignKey(FeeRecord, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.fee_record.student.get_full_name() or self.fee_record.student.username} - ₹{self.amount} on {self.payment_date}"

class PaymentDetails(models.Model):
    qr_code = models.ImageField(upload_to='fees_qr/', blank=True, null=True)
    account_number = models.CharField(max_length=32, blank=True)
    ifsc_code = models.CharField(max_length=16, blank=True)
    upi_id = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return "Current Payment Details"

class Notification(models.Model):
    PAYMENT_RECEIVED = 'payment_received'
    PAYMENT_APPROVED = 'payment_approved'
    PAYMENT_REJECTED = 'payment_rejected'
    OUTING_REQUESTED = 'outing_requested'
    OUTING_APPROVED = 'outing_approved'
    OUTING_REJECTED = 'outing_rejected'
    
    NOTIFICATION_TYPES = [
        (PAYMENT_RECEIVED, 'Payment Received'),
        (PAYMENT_APPROVED, 'Payment Approved'),
        (PAYMENT_REJECTED, 'Payment Rejected'),
        (OUTING_REQUESTED, 'Outing Requested'),
        (OUTING_APPROVED, 'Outing Approved'),
        (OUTING_REJECTED, 'Outing Rejected'),
    ]

    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    payment = models.ForeignKey('FeePayment', on_delete=models.CASCADE, null=True, blank=True)
    outing_request = models.ForeignKey('outings.OutingRequest', on_delete=models.CASCADE, null=True, blank=True)
    outing = models.ForeignKey('outings.Outing', on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Payment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    # Add other fields as needed

    def __str__(self):
        return f"{self.student} paid {self.amount} on {self.created_at}"
