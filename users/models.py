# Create your models here.
# Database tables (User, Therapist, Patient)

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    Adds user_type field to distinguish between Therapists and Patients.
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
    
    # Use email for login instead of username
    email = models.EmailField(unique=True)
    
    # USERNAME_FIELD tells Django to use email for authentication
    USERNAME_FIELD = 'email'
    
    # REQUIRED_FIELDS are prompted for when creating superuser
    # email is already the USERNAME_FIELD, so don't include it here
    REQUIRED_FIELDS = ['username', 'user_type']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"