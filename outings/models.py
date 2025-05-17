from django.db import models
from django.conf import settings
from django.utils import timezone

class Outing(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='outings')
    purpose = models.TextField()
    destination = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_regular_outings'
    )
    rejection_reason = models.TextField(blank=True)
    actual_return_time = models.DateTimeField(null=True, blank=True)
    parent_email = models.EmailField("Parent Email", max_length=254, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        # Use get_full_name() if it returns a non-empty string, otherwise use username
        full_name = self.student.get_full_name() if hasattr(self.student, 'get_full_name') else ''
        return f"{full_name or self.student.username} - {self.destination}"

    def is_overdue(self):
        if self.status == 'approved' and self.actual_return_time is None:
            return timezone.now() > self.end_time
        return False

class OutingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='outing_requests')
    date = models.DateField()
    out_time = models.TimeField()
    in_time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_outing_requests'
    )
    rejection_reason = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date', '-out_time']
        verbose_name = 'Outing Request'
        verbose_name_plural = 'Outing Requests'

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date} ({self.get_status_display()})"

    def is_pending(self):
        return self.status == 'pending'

    def is_approved(self):
        return self.status == 'approved'

    def is_rejected(self):
        return self.status == 'rejected' 