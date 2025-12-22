# Create your models here.
# Database tables (User, Therapist, Patient)
"""
Models for Quipster app:
- CustomUser extends AbstractUser with a user_type field (Therapist/Patient)
- TherapistProfile and PatientProfile store related information
- Default login uses username and password (change USERNAME_FIELD for email login)
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    Keeps username/password login for now, email is optional.
    - Authentication identity lives here
    - Human-readable names, DOB, email
    """
    
    USER_TYPE_CHOICES = [
        ('THERAPIST', 'Occupational Therapist'),
        ('PATIENT', 'Patient'),
    ]
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        help_text="User role: Therapist or Patient"
    )
    
    # Email optional for now
    email = models.EmailField(unique=True, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Keep default login with username
    # USERNAME_FIELD = 'username'

    # Required fields for creating superuser
    REQUIRED_FIELDS = ['user_type']

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    


class TherapistProfile(models.Model):
    """
    Professional metadata for therapists.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50, unique=True)
    max_caseload = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVE', 'Active'),
            ('INACTIVE', 'Inactive'),
            ('ON_LEAVE', 'On Leave'),
        ],
        default='ACTIVE'
    )

    def __str__(self):
        return f"{self.user.username} - {self.license_number}"


class PatientProfile(models.Model):
    """
    Clinical metadata for patients.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    assigned_therapist = models.ForeignKey(
        TherapistProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    medical_record_number = models.CharField(max_length=50, unique=True)
    admission_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVE', 'Active'),
            ('DISCHARGED', 'Discharged'),
        ],
        default='ACTIVE'
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.full_name} – MRN {self.medical_record_number}"

