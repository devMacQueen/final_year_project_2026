from django.db import models
from accounts.models import User
import random
import string
from accounts.models import AccountStatus

FACULTY_CHOICES = [
    ('FNAS', 'Faculty of Natural & Applied Science'),
    ('FHS', 'Faculty of Health Science'),
    ('FSS', 'Faculty of Social Science'),
    ('FMS', 'Faculty of Management Science'),
    ('FAS', 'Faculty of Art'),
    ('FAGR', 'Faculty of Agricultural Science'),
]

BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
]

GENOTYPE_CHOICES = [
    ('AA', 'AA'), ('AS', 'AS'),
    ('SS', 'SS'), ('AC', 'AC'),
]

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    matric_number = models.CharField(max_length=50, unique=True)
    faculty = models.CharField(max_length=10, choices=FACULTY_CHOICES)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[
        ('male','Male'),
        ('female','Female'),
        ('other','Other')
    ])
    phone = models.CharField(max_length=20)
    address = models.TextField()

    # Medical History
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    genotype = models.CharField(max_length=5, choices=GENOTYPE_CHOICES, blank=True)
    allergies = models.TextField(blank=True, help_text='List any known allergies')
    chronic_conditions = models.TextField(blank=True, help_text='e.g. Diabetes, Asthma, Hypertension')
    current_medications = models.TextField(blank=True, help_text='Any medications currently taking')

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)

    smartcard_id = models.CharField(max_length=20, unique=True, blank=True)
    biometric_pin = models.CharField(max_length=6, blank=True,  null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    account_status = models.CharField(
    max_length=20,
    choices=AccountStatus.choices,
    default=AccountStatus.ACTIVE,
    )
    status_reason  = models.TextField(blank=True, null=True)
    status_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.smartcard_id:
            self.smartcard_id = 'SC-' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)

    def get_faculty_display_name(self):
        for code, name in FACULTY_CHOICES:
            if code == self.faculty:
                return name
        return self.faculty

    def __str__(self):
        return f"{self.full_name} ({self.matric_number})"


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='records')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    diagnosis = models.TextField()
    prescription = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Record for {self.patient.full_name} on {self.created_at.date()}"


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    decline_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.full_name} - {self.date} ({self.status})"
