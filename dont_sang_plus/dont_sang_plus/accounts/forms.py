from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

# ...le reste du code reste identique...

class DonorSignUpForm(UserCreationForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True, label="Date de naissance")
    phone = forms.CharField(required=True, label="Téléphone")
    address = forms.CharField(required=True, label="Adresse")
    city = forms.CharField(required=True, label="Ville")
    blood_type = forms.ChoiceField(choices=CustomUser.BLOOD_TYPE_CHOICES, required=True, label="Groupe sanguin")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'birth_date',
                  'phone', 'address', 'city', 'blood_type', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'donor'
        if commit:
            user.save()
        return user

class HospitalSignUpForm(UserCreationForm):
    hospital_name = forms.CharField(required=True, label="Nom de l'établissement")
    phone = forms.CharField(required=True, label="Téléphone")
    address = forms.CharField(required=True, label="Adresse")
    city = forms.CharField(required=True, label="Ville")
    contact_email = forms.EmailField(required=True, label="Email de contact")
    contact_phone = forms.CharField(required=True, label="Téléphone de contact")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'hospital_name', 'phone', 'address',
                  'city', 'contact_email', 'contact_phone', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'hospital'
        if commit:
            user.save()
        return user