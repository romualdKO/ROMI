from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from .models import BloodRequest, DonationResponse, DonorAvailability

User = get_user_model()

class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = ['blood_type', 'quantity', 'urgency', 'address', 'city', 'deadline', 'description']
        
        widgets = {
            'blood_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100,
                'step': 1,
                'placeholder': 'Nombre de poches de sang nécessaires'
            }),
            'urgency': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adresse complète de l\'hôpital',
                'required': True
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ville',
                'required': True
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Détails sur le patient, raison de la demande, instructions spéciales...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Labels personnalisés
        self.fields['blood_type'].label = "Groupe sanguin requis"
        self.fields['quantity'].label = "Quantité (poches de sang)"
        self.fields['urgency'].label = "Niveau d'urgence"
        self.fields['address'].label = "Adresse de l'hôpital"
        self.fields['city'].label = "Ville"
        self.fields['deadline'].label = "Date et heure limite"
        self.fields['description'].label = "Description / Informations complémentaires"
        
        # Champs obligatoires
        required_fields = ['blood_type', 'quantity', 'urgency', 'address', 'city', 'deadline']
        for field in required_fields:
            self.fields[field].required = True

    def clean_quantity(self):
        """Validation pour la quantité"""
        quantity = self.cleaned_data.get('quantity')
        
        if quantity is None:
            raise forms.ValidationError("La quantité est obligatoire.")
        
        if quantity < 1:
            raise forms.ValidationError("La quantité doit être d'au moins 1 poche.")
        
        if quantity > 100:
            raise forms.ValidationError("La quantité ne peut pas dépasser 100 poches.")
        
        return quantity

    def clean_deadline(self):
        """Validation pour la date limite"""
        from django.utils import timezone
        deadline = self.cleaned_data.get('deadline')
        
        if deadline and deadline <= timezone.now():
            raise forms.ValidationError("La date limite doit être dans le futur.")
        
        return deadline

class DonationResponseForm(forms.ModelForm):
    class Meta:
        model = DonationResponse
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Message au personnel hospitalier (optionnel)...'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].label = "Message (optionnel)"
        self.fields['message'].required = False

# ✅ FORMULAIRE CORRIGÉ POUR LA DISPONIBILITÉ
class AvailabilityUpdateForm(forms.ModelForm):
    class Meta:
        model = DonorAvailability
        fields = ['is_available', 'next_available_date', 'notes']
        widgets = {
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'next_available_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Raison de l\'indisponibilité, contraintes horaires, informations importantes...'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_available'].label = "Je suis disponible pour donner du sang"
        self.fields['next_available_date'].label = "Prochaine date de disponibilité"
        self.fields['notes'].label = "Notes personnelles"
        self.fields['next_available_date'].required = False
        self.fields['notes'].required = False

class DonorAvailabilityForm(forms.ModelForm):
    class Meta:
        model = DonorAvailability
        fields = ['is_available', 'next_available_date', 'notes']
        widgets = {
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'next_available_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes sur votre disponibilité...'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_available'].label = "Je suis disponible pour donner"
        self.fields['next_available_date'].label = "Prochaine date de disponibilité"
        self.fields['notes'].label = "Notes"

# ✅ FORMULAIRE CORRIGÉ POUR LE PROFIL UTILISATEUR
class UserProfileForm(forms.ModelForm):
    # Champs additionnels pour le formulaire
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User  # ✅ SPÉCIFIE LE MODÈLE USER
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'city', 'address', 
            'birth_date', 'blood_type', 'medical_history', 'profile_picture'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+225 XX XX XX XX XX'
            }),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Votre adresse complète...'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'blood_type': forms.Select(attrs={'class': 'form-select'}),
            'medical_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Allergies, conditions médicales, traitements en cours, dernière donation...'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Appliquer les classes CSS à tous les champs
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})
            
        # Rendre certains champs optionnels selon le type d'utilisateur
        if hasattr(self.instance, 'user_type') and self.instance.user_type == 'hospital':
            # Pour les hôpitaux, masquer les champs spécifiques aux donneurs
            if 'blood_type' in self.fields:
                del self.fields['blood_type']
            if 'birth_date' in self.fields:
                del self.fields['birth_date']
            if 'medical_history' in self.fields:
                del self.fields['medical_history']
        
        # Labels personnalisés
        self.fields['first_name'].label = "Prénom"
        self.fields['last_name'].label = "Nom"
        self.fields['email'].label = "Email"
        self.fields['phone'].label = "Téléphone"
        self.fields['city'].label = "Ville"
        self.fields['address'].label = "Adresse"
        
        if 'birth_date' in self.fields:
            self.fields['birth_date'].label = "Date de naissance"
        if 'blood_type' in self.fields:
            self.fields['blood_type'].label = "Groupe sanguin"
        if 'medical_history' in self.fields:
            self.fields['medical_history'].label = "Antécédents médicaux"
        if 'profile_picture' in self.fields:
            self.fields['profile_picture'].label = "Photo de profil"

    def save(self, commit=True):
        """Sauvegarder les données du formulaire"""
        user = super().save(commit=False)
        
        # Mettre à jour les champs User standard
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        
        if commit:
            user.save()
        return user