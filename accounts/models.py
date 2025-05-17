from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', _('Student')
        WARDEN = 'WARDEN', _('Warden')
        ADMIN = 'ADMIN', _('Admin')
        SECURITY = 'SECURITY', _('Security Staff')

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_warden(self):
        return self.role == self.Role.WARDEN

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_security(self):
        return self.role == self.Role.SECURITY
