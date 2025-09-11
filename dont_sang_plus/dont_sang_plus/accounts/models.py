# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('donor', 'Donneur'),
        ('hospital', 'Hôpital'),
    ]
    
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'En attente de vérification'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    # Rendre l'email unique
    email = models.EmailField(unique=True, verbose_name="Email")
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    HOSPITAL_TYPE_CHOICES = [
        ('public', 'Hôpital public'),
        ('private', 'Clinique privée'),
        ('chu', 'CHU (Centre Hospitalier Universitaire)'),
        ('military', 'Hôpital militaire'),
        ('other', 'Autre'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    city = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Champs spécifiques aux donneurs
    blood_type = models.CharField(max_length=3, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True, verbose_name="Antécédents médicaux")  # ✅ AJOUTE CETTE LIGNE
    # Champs spécifiques aux hôpitaux
    hospital_name = models.CharField(max_length=200, blank=True)
    hospital_type = models.CharField(
        max_length=50, 
        choices=HOSPITAL_TYPE_CHOICES,  # ✅ AJOUTE LES CHOICES
        blank=True
    )
    address = models.TextField(blank=True)
    
    # ✅ NOUVEAUX CHAMPS POUR LA VÉRIFICATION
    is_verified = models.BooleanField(default=False, verbose_name="Vérifié")
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending',
        verbose_name="Statut de vérification"
    )
    hospital_license_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name="Numéro de licence hôpital"
    )
    verification_notes = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Notes de vérification (admin)"
    )
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Vérifié le")
    verified_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Vérifié par"
    )
    
    def __str__(self):
        if self.user_type == 'hospital':
            return f"{self.hospital_name} - {self.email}"
        return f"{self.get_full_name()} - {self.email}"
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
    
    # Configuration pour utiliser l'email comme identifiant de connexion
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']