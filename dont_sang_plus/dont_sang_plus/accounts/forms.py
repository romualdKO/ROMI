# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class DonorSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    blood_type = forms.ChoiceField(choices=CustomUser.BLOOD_TYPE_CHOICES, required=True)
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
    city = forms.CharField(max_length=100, required=True)
    phone = forms.CharField(max_length=20, required=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'email', 'password1', 'password2',
            'blood_type', 'birth_date', 'city', 'phone'
        ]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Un compte avec cette adresse email existe déjà.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)  # ✅ CORRECT
        user.user_type = 'donor'
        user.email = self.cleaned_data['email']
        user.blood_type = self.cleaned_data['blood_type']
        user.birth_date = self.cleaned_data['birth_date']
        user.city = self.cleaned_data['city']
        user.phone = self.cleaned_data['phone']
        
        if commit:
            user.save()
        return user

class HospitalSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    hospital_name = forms.CharField(max_length=200, required=True, label="Nom de l'hôpital")
    hospital_type = forms.ChoiceField(
        choices=[
            ('public', 'Hôpital public'),
            ('private', 'Clinique privée'),
            ('chu', 'CHU (Centre Hospitalier Universitaire)'),
            ('military', 'Hôpital militaire'),
            ('other', 'Autre'),
        ],
        required=True,
        label="Type d'établissement"
    )
    city = forms.CharField(max_length=100, required=True, label="Ville")
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        label="Adresse complète"
    )
    phone = forms.CharField(max_length=20, required=True, label="Téléphone")
    hospital_license_number = forms.CharField(
        max_length=50,
        required=False,
        label="Numéro de licence (optionnel)",
        help_text="Si disponible, cela accélérera la vérification"
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'email', 'password1', 'password2',
            'hospital_name', 'hospital_type', 'city', 'address', 'phone', 'hospital_license_number'
        ]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Un compte avec cette adresse email existe déjà.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)  # ✅ CORRECT - ne pas appeler CustomUser()
        user.user_type = 'hospital'
        user.email = self.cleaned_data['email']
        user.hospital_name = self.cleaned_data['hospital_name']
        user.hospital_type = self.cleaned_data['hospital_type']
        user.city = self.cleaned_data['city']
        user.address = self.cleaned_data['address']
        user.phone = self.cleaned_data['phone']
        user.hospital_license_number = self.cleaned_data['hospital_license_number']
        
        if commit:
            user.save()
        return user