# hospitals/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class HospitalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'hospital'})
    description = models.TextField(blank=True)
    services = models.TextField(blank=True, help_text="Services offerts par l'hôpital")
    opening_hours = models.TextField(blank=True)
    website = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Profil de {self.user.hospital_name}"

class BloodStock(models.Model):
    hospital = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'hospital'})
    o_plus = models.PositiveIntegerField(default=0)
    o_minus = models.PositiveIntegerField(default=0)
    a_plus = models.PositiveIntegerField(default=0)
    a_minus = models.PositiveIntegerField(default=0)
    b_plus = models.PositiveIntegerField(default=0)
    b_minus = models.PositiveIntegerField(default=0)
    ab_plus = models.PositiveIntegerField(default=0)
    ab_minus = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Stock de sang de {self.hospital.hospital_name}"
    
    def get_stock_level(self, blood_type):
        return getattr(self, blood_type.lower().replace('+', '_plus').replace('-', '_minus'), 0)
    
    def update_stock(self, blood_type, quantity):
        field_name = blood_type.lower().replace('+', '_plus').replace('-', '_minus')
        if hasattr(self, field_name):
            setattr(self, field_name, max(0, getattr(self, field_name) + quantity))
            self.save()