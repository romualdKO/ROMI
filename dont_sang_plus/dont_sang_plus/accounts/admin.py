# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import DonorSignUpForm, HospitalSignUpForm

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'city', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('user_type', 'phone', 'address', 'city', 
                      'blood_type', 'birth_date', 'medical_history', 'last_donation',
                      'hospital_name', 'contact_email', 'contact_phone')
        }),
    )
    
    # Pour séparer les champs selon le type d'utilisateur lors de la création
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'user_type'),
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        if not obj:  # Lors de la création d'un nouvel utilisateur
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

admin.site.register(CustomUser, CustomUserAdmin)