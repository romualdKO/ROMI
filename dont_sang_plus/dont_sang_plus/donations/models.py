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
    
    def is_currently_available(self):
        """
        Vérifie si le donneur est vraiment disponible aujourd'hui.
        Prend en compte à la fois is_available ET next_available_date.
        """
        from django.utils import timezone
        today = timezone.now().date()
        
        # Si explicitement marqué comme indisponible
        if not self.is_available:
            return False
        
        # Si la date de prochaine disponibilité est dans le futur
        if self.next_available_date and self.next_available_date > today:
            return False
        
        return True
    
    def auto_unlock(self):
        """
        Débloque automatiquement le donneur si la date de disponibilité est passée.
        Retourne True si le déblocage a été effectué.
        """
        from django.utils import timezone
        today = timezone.now().date()
        
        # Si la date est passée ou égale à aujourd'hui
        if self.next_available_date and self.next_available_date <= today:
            self.is_available = True
            self.next_available_date = None
            self.save()
            return True
        
        return False
    
    def get_lock_reason(self):
        """
        Retourne la raison pour laquelle le donneur est indisponible.
        Utile pour afficher des messages personnalisés.
        """
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.is_currently_available():
            today = timezone.now().date()
            
            if self.next_available_date and self.next_available_date > today:
                days_remaining = (self.next_available_date - today).days
                return f"Vous devez attendre jusqu'au {self.next_available_date.strftime('%d/%m/%Y')} ({days_remaining} jour{'s' if days_remaining > 1 else ''} restant{'s' if days_remaining > 1 else ''})"
            
            elif not self.is_available:
                return "Vous êtes actuellement marqué comme indisponible"
        
        return None


# ========================================
# SYSTÈME DE RÉCOMPENSES ET CLASSEMENT
# ========================================

class DonorRanking(models.Model):
    """Classement et statistiques des donneurs"""
    TIER_CHOICES = (
        ('standard', 'Standard'),
        ('bronze', 'Bronze'),
        ('silver', 'Argent'),
        ('gold', 'Or'),
        ('platinum', 'Platine'),
    )
    
    donor = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'donor'}, related_name='ranking')
    total_donations = models.PositiveIntegerField(default=0, help_text="Nombre total de dons complétés")
    current_tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='standard')
    last_donation_date = models.DateField(null=True, blank=True)
    points = models.PositiveIntegerField(default=0, help_text="Points cumulés")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-total_donations', '-points']
        verbose_name = "Classement Donneur"
        verbose_name_plural = "Classements Donneurs"
    
    def update_tier(self):
        """Met à jour automatiquement le tier basé sur le nombre de dons"""
        if self.total_donations >= 20:
            self.current_tier = 'platinum'
        elif self.total_donations >= 10:
            self.current_tier = 'gold'
        elif self.total_donations >= 5:
            self.current_tier = 'silver'
        elif self.total_donations >= 2:
            self.current_tier = 'bronze'
        else:
            self.current_tier = 'standard'
        self.save()
    
    def get_discount_rate(self):
        """Retourne le taux de réduction selon le tier"""
        discount_map = {
            'standard': 0,
            'bronze': 5,
            'silver': 10,
            'gold': 15,
            'platinum': 20,
        }
        return discount_map.get(self.current_tier, 0)
    
    def __str__(self):
        return f"{self.donor.get_full_name()} - {self.current_tier.upper()} ({self.total_donations} dons)"


class HospitalBenefit(models.Model):
    """Avantages offerts par les hôpitaux aux donneurs"""
    hospital = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'hospital'}, related_name='benefits')
    title = models.CharField(max_length=200, help_text="Ex: Consultation gratuite")
    description = models.TextField()
    minimum_tier = models.CharField(max_length=20, choices=DonorRanking.TIER_CHOICES, default='bronze')
    discount_percentage = models.PositiveIntegerField(help_text="Pourcentage de réduction (0-100)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-discount_percentage']
        verbose_name = "Avantage Hôpital"
        verbose_name_plural = "Avantages Hôpitaux"
    
    def __str__(self):
        return f"{self.title} - {self.hospital.hospital_name}"


class DonorVoucher(models.Model):
    """Bons de réduction pour les donneurs"""
    donor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'donor'}, related_name='vouchers')
    hospital = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'hospital'}, related_name='issued_vouchers')
    benefit = models.ForeignKey(HospitalBenefit, on_delete=models.SET_NULL, null=True, blank=True)
    voucher_code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.PositiveIntegerField()
    valid_until = models.DateField()
    is_used = models.BooleanField(default=False)
    used_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Bon de Réduction"
        verbose_name_plural = "Bons de Réduction"
    
    def is_valid(self):
        """Vérifie si le bon est encore valide"""
        from django.utils import timezone
        return not self.is_used and self.valid_until >= timezone.now().date()
    
    def __str__(self):
        return f"Bon {self.voucher_code} - {self.discount_percentage}%"