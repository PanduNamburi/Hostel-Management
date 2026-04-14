from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from accounts.models import CustomUser
from .models import FeeRecord
from decimal import Decimal
from datetime import timedelta

@receiver(post_save, sender=CustomUser)
def create_student_fee_record(sender, instance, created, **kwargs):
    if created and instance.role == CustomUser.Role.STUDENT:
        # Check if one somehow already exists
        if not FeeRecord.objects.filter(student=instance).exists():
            FeeRecord.objects.create(
                student=instance,
                fee_amount=Decimal('100000.00'),
                due_date=timezone.now().date() + timedelta(days=30),
                status='unpaid'
            )
