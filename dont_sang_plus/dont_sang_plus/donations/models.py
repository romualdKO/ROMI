from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class BloodRequest(models.Model):
    URGENCY_CHOICES = (
        ('immediate', 'Immédiat (urgence vitale)'),
        ('24h', 'Dans les 24h'),
        ('planned', 'Planifié'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('completed', 'Effectué'),
        ('cancelled', 'Annulé'),
        ('rejected', 'Rejeté'),
    )
    
    hospital = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'hospital'})
    blood_type = models.CharField(max_length=3, choices=User.BLOOD_TYPE_CHOICES)
    quantity = models.PositiveIntegerField(help_text="Nombre de poches de sang nécessaires")
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    deadline = models.DateTimeField()
    description = models.TextField(blank=True)
    is_fulfilled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @staticmethod
    def get_compatible_donors(blood_type):
        """Retourne les groupes sanguins qui peuvent donner à ce type"""
        compatibility_map = {
            'A+': ['A+', 'A-', 'O+', 'O-'],
            'A-': ['A-', 'O-'],
            'B+': ['B+', 'B-', 'O+', 'O-'],
            'B-': ['B-', 'O-'],
            'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],  # Receveur universel
            'AB-': ['A-', 'B-', 'AB-', 'O-'],
            'O+': ['O+', 'O-'],
            'O-': ['O-'],
        }
        return compatibility_map.get(blood_type, [])
    
    @staticmethod
    def get_compatible_recipients(donor_blood_type):
        """Retourne les groupes sanguins qui peuvent recevoir de ce donneur"""
        compatibility_map = {
            'O-': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],  # Donneur universel
            'O+': ['A+', 'B+', 'AB+', 'O+'],
            'A-': ['A+', 'A-', 'AB+', 'AB-'],
            'A+': ['A+', 'AB+'],
            'B-': ['B+', 'B-', 'AB+', 'AB-'],
            'B+': ['B+', 'AB+'],
            'AB-': ['AB+', 'AB-'],
            'AB+': ['AB+'],
        }
        return compatibility_map.get(donor_blood_type, [])
    
    def get_compatible_donors_queryset(self):
        """Retourne les donneurs compatibles pour cette demande"""
        compatible_types = self.get_compatible_donors(self.blood_type)
        return User.objects.filter(
            user_type='donor',
            blood_type__in=compatible_types,
            is_active=True
        )
    
    def __str__(self):
        return f"Demande de {self.blood_type} par {self.hospital.hospital_name}"
    
class Donation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('scheduled', 'Programmé'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    )
    
    donor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'donor'})
    blood_request = models.ForeignKey('BloodRequest', on_delete=models.CASCADE)
    donation_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Don de {self.donor.username} pour {self.blood_request}"

class DonationResponse(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('accepted', 'Accepté'),
        ('rejected', 'Refusé'),
        ('completed', 'Terminé'),
        ('unsatisfied', 'Insatisfait'),
    )
    
    donor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'donor'})
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_date = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, help_text="Message au donneur")
    
    class Meta:
        unique_together = ['donor', 'blood_request']
    
    def __str__(self):
        return f"Réponse de {self.donor.username} à {self.blood_request}"

class ChatMessage(models.Model):
    donation_response = models.ForeignKey(DonationResponse, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Message de {self.sender.username}"

class DonorAvailability(models.Model):
    donor = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'donor'})
    is_available = models.BooleanField(default=True)
    next_available_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Disponibilité de {self.donor.username}"