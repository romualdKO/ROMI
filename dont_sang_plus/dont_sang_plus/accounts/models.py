# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('donor', 'Donneur'),
        ('hospital', 'Hôpital'),
        ('admin', 'Administrateur'),
    )
    BLOOD_TYPE_CHOICES = (
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='donor')
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Champs spécifiques aux donneurs
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    medical_history = models.TextField(blank=True)
    last_donation = models.DateField(null=True, blank=True)
    
    # Champs spécifiques aux hôpitaux
    hospital_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        if self.user_type == 'hospital' and self.hospital_name:
            return f"{self.hospital_name}"
        return f"{self.username} ({self.get_user_type_display()})"