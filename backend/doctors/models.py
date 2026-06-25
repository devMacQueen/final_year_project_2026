from django.db import models
from accounts.models import User
from accounts.models import AccountStatus

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    specialization = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    account_status = models.CharField(
    max_length=20,
    choices=AccountStatus.choices,
    default=AccountStatus.ACTIVE,
    )
    status_reason  = models.TextField(blank=True, null=True)
    status_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.full_name} ({self.specialization})"
