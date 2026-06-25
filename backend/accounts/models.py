from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"


class AccountStatus(models.TextChoices):
    ACTIVE      = 'active',      'Active'
    SUSPENDED   = 'suspended',   'Suspended'
    DEACTIVATED = 'deactivated', 'Deactivated'


class OTPRecord(models.Model):
    OTP_EXPIRY_MINUTES = 5

    user       = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.CASCADE,
                     related_name='otp_records'
                 )
    otp_code   = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used    = models.BooleanField(default=False)

    def is_valid(self):
        expiry = self.created_at + timedelta(minutes=self.OTP_EXPIRY_MINUTES)
        return not self.is_used and timezone.now() < expiry

    def seconds_remaining(self):
        expiry = self.created_at + timedelta(minutes=self.OTP_EXPIRY_MINUTES)
        delta  = (expiry - timezone.now()).total_seconds()
        return max(0, int(delta))

    @classmethod
    def generate_for(cls, user):
        cls.objects.filter(user=user).delete()
        code = str(random.randint(100000, 999999))
        return cls.objects.create(user=user, otp_code=code)

    def __str__(self):
        return f"OTP({self.otp_code}) for {self.user.username}"

    class Meta:
        verbose_name = "OTP Record"
        ordering     = ['-created_at']