from django.db import models
from django.conf import settings

class Attendance(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    total_periods = models.PositiveIntegerField(default=8)
    absent_periods = models.PositiveIntegerField(default=0)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='marked_attendance')
    marked_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', '-marked_at']
        unique_together = ['student', 'date']

    @property
    def present_periods(self):
        return self.total_periods - self.absent_periods

    @property
    def attendance_percentage(self):
        if self.total_periods == 0:
            return 0
        return round((self.present_periods / self.total_periods) * 100, 2)

    def __str__(self):
        return f"{self.student.get_full_name() or self.student.username} - {self.date} - {self.attendance_percentage}%" 