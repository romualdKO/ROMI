from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse

from .models import CustomUser
# ✅ CORRIGE L'IMPORT DES FORMULAIRES
from .forms import DonorSignUpForm, HospitalSignUpForm

def custom_login(request):
    """Vue personnalisée pour la connexion"""
    if request.method == 'POST':
        email = request.POST.get('username')  # Le champ s'appelle username mais contient l'email
        password = request.POST.get('password')
        
        print(f"DEBUG: Tentative de connexion - Email: {email}")
        
        # Authentification avec l'email
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            print(f"DEBUG: Utilisateur trouvé - {user.email}, Type: {user.user_type}")
            
            # Vérification pour les hôpitaux
            if user.user_type == 'hospital':
                if not user.is_verified or user.verification_status != 'approved':
                    messages.error(request, 
                        "🏥 Votre compte hôpital n'est pas encore validé. "
                        "Vous recevrez un email dès que la vérification sera terminée."
                    )
                    print("DEBUG: Hôpital non vérifié")
                    form = AuthenticationForm()
                    return render(request, 'accounts/login.html', {'form': form})
            
            # Connexion réussie
            login(request, user)
            print(f"DEBUG: Connexion réussie pour {user.email}")
            
            # Redirection selon le type d'utilisateur
            if user.user_type == 'donor':
                messages.success(request, f"🩸 Bienvenue {user.get_full_name()} !")
                print("DEBUG: Redirection vers donor dashboard")
                return redirect('donations:donor_dashboard')
            elif user.user_type == 'hospital':
                messages.success(request, f"🏥 Bienvenue {user.hospital_name} !")
                print("DEBUG: Redirection vers hospital dashboard")
                return redirect('donations:hospital_dashboard')
            else:
                print("DEBUG: Redirection vers home")
                return redirect('home')
        else:
            print("DEBUG: Échec de l'authentification")
            messages.error(request, "❌ Nom d'utilisateur ou mot de passe incorrect.")
    
    form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def custom_logout(request):
    """Vue personnalisée pour la déconnexion"""
    logout(request)
    messages.success(request, "👋 Vous avez été déconnecté avec succès.")
    return redirect('accounts:login')

def donor_signup(request):
    """Vue pour l'inscription des donneurs"""
    if request.method == 'POST':
        # ✅ UTILISE LE BON NOM DE FORMULAIRE
        form = DonorSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.user_type = 'donor'
                    user.is_verified = True  # Les donneurs sont validés automatiquement
                    user.verification_status = 'approved'
                    user.is_active = True
                    user.save()
                    
                    print(f"DEBUG: Donneur créé - {user.get_full_name()}")
                    
                    # Email de bienvenue au donneur
                    try:
                        send_mail(
                            subject='🩸 Bienvenue dans Don Sang Plus !',
                            message=f'Bonjour {user.get_full_name()},\n\n'
                                   f'Votre compte donneur a été créé avec succès !\n\n'
                                   f'📋 Vos informations :\n'
                                   f'• Nom : {user.get_full_name()}\n'
                                   f'• Groupe sanguin : {user.blood_type}\n'
                                   f'• Ville : {user.city}\n\n'
                                   f'🎯 Vous pouvez maintenant vous connecter et commencer à sauver des vies !\n\n'
                                   f'🔗 Connexion : {request.build_absolute_uri("/accounts/login/")}\n\n'
                                   f'Merci de votre générosité !\n'
                                   f'Équipe Don Sang Plus',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=True,
                        )
                        print("DEBUG: Email bienvenue donneur envoyé")
                    except Exception as e:
                        print(f"ERREUR EMAIL DONNEUR: {e}")
                    
                    messages.success(request, 
                        f"✅ Compte créé avec succès ! Bienvenue {user.get_full_name()}. "
                        "Vous pouvez maintenant vous connecter."
                    )
                    return redirect('accounts:login')
            except Exception as e:
                print(f"Erreur lors de la création du compte donneur: {e}")
                messages.error(request, "❌ Erreur lors de la création du compte. Veuillez réessayer.")
    else:
        # ✅ UTILISE LE BON NOM DE FORMULAIRE
        form = DonorSignUpForm()
    
    context = {
        'form': form,
        'title': '🩸 Inscription Donneur',
        'signup_type': 'donor',
        'btn_class': 'btn-danger',
        'btn_text': 'Créer mon compte donneur'
    }
    return render(request, 'accounts/signup.html', context)

def hospital_signup(request):
    """Vue pour l'inscription des hôpitaux"""
    if request.method == 'POST':
        # ✅ UTILISE LE BON NOM DE FORMULAIRE
        form = HospitalSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.user_type = 'hospital'
                    user.is_verified = False  # Les hôpitaux doivent être validés
                    user.verification_status = 'pending'
                    user.is_active = True
                    user.save()
                    
                    print(f"DEBUG: Hôpital créé - {user.hospital_name}")
                    
                    # Email automatique à l'admin
                    try:
                        print("DEBUG: Tentative d'envoi email admin...")
                        
                        send_mail(
                            subject='🚨 NOUVEAU HÔPITAL À VALIDER - URGENT',
                            message=f'⚠️ NOUVELLE DEMANDE DE VALIDATION :\n\n'
                                   f'🏥 Hôpital : {user.hospital_name}\n'
                                   f'📧 Email : {user.email}\n'
                                   f'📱 Téléphone : {user.phone}\n'
                                   f'📍 Ville : {user.city}\n'
                                   f'🏷️ Type : {user.get_hospital_type_display()}\n'
                                   f'📄 Licence : {user.hospital_license_number or "Non fournie"}\n'
                                   f'📅 Date : {timezone.now().strftime("%d/%m/%Y %H:%M")}\n\n'
                                   f'👉 VALIDER ICI : {request.build_absolute_uri("/admin/accounts/customuser/")}\n\n'
                                   f'🔗 Lien direct : {request.build_absolute_uri(f"/admin/accounts/customuser/{user.id}/change/")}\n\n'
                                   f'Don Sang Plus Admin',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=['romualdndri9@gmail.com'],
                            fail_silently=False,
                        )
                        print("DEBUG: Email admin envoyé avec succès")
                        
                    except Exception as e:
                        print(f"ERREUR EMAIL ADMIN: {e}")
                        messages.warning(request, f"Inscription réussie mais email admin non envoyé: {e}")
                    
                    # Email de confirmation au demandeur
                    try:
                        print("DEBUG: Tentative d'envoi email confirmation...")
                        
                        send_mail(
                            subject='🏥 Inscription en attente de validation - Don Sang Plus',
                            message=f'Bonjour {user.get_full_name()},\n\n'
                                   f'Votre demande d\'inscription pour {user.hospital_name} '
                                   f'a été reçue et est en cours de vérification par notre équipe.\n\n'
                                   f'📋 Informations soumises :\n'
                                   f'• Hôpital : {user.hospital_name}\n'
                                   f'• Type : {user.get_hospital_type_display()}\n'
                                   f'• Ville : {user.city}\n\n'
                                   f'⏳ La vérification prend généralement 24-48h.\n'
                                   f'📧 Vous recevrez un email de confirmation dès validation.\n\n'
                                   f'Merci de votre patience !\n'
                                   f'Équipe Don Sang Plus',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=False,
                        )
                        print("DEBUG: Email confirmation envoyé avec succès")
                        
                    except Exception as e:
                        print(f"ERREUR EMAIL CONFIRMATION: {e}")
                    
                    messages.success(request, 
                        "🎉 Inscription enregistrée avec succès ! "
                        "Votre compte sera activé après vérification par notre équipe. "
                        "Vous recevrez un email de confirmation dans les 24-48h."
                    )
                    return redirect('accounts:login')
            except Exception as e:
                print(f"Erreur lors de la création du compte hôpital: {e}")
                messages.error(request, "❌ Erreur lors de la création du compte. Veuillez réessayer.")
    else:
        # ✅ UTILISE LE BON NOM DE FORMULAIRE
        form = HospitalSignUpForm()
    
    context = {
        'form': form,
        'title': '🏥 Inscription Hôpital',
        'signup_type': 'hospital',
        'btn_class': 'btn-info',
        'btn_text': 'Soumettre ma demande'
    }
    return render(request, 'accounts/signup.html', context)

@login_required
def dashboard(request):
    """Redirection automatique selon le type d'utilisateur"""
    if request.user.user_type == 'donor':
        return redirect('donations:donor_dashboard')
    elif request.user.user_type == 'hospital':
        return redirect('donations:hospital_dashboard')
    else:
        return redirect('home')

def is_admin(user):
    """Vérification si l'utilisateur est admin"""
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def quick_validate_hospital(request, user_id):
    """Validation rapide d'un hôpital par l'admin"""
    hospital = get_object_or_404(CustomUser, id=user_id, user_type='hospital')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            if action == 'approve':
                hospital.verification_status = 'approved'
                hospital.is_verified = True
                hospital.verified_at = timezone.now()
                hospital.verified_by = request.user
                hospital.save()
                
                # Email de validation
                send_mail(
                    subject='✅ Compte validé - Don Sang Plus',
                    message=f'Bonjour {hospital.get_full_name()},\n\n'
                           f'Excellente nouvelle ! Votre compte pour {hospital.hospital_name} '
                           f'a été validé avec succès.\n\n'
                           f'🎉 Vous pouvez maintenant vous connecter et utiliser toutes les fonctionnalités :\n'
                           f'• Créer des demandes de sang\n'
                           f'• Communiquer avec les donneurs\n'
                           f'• Gérer vos demandes\n\n'
                           f'🔗 Connexion : {request.build_absolute_uri("/accounts/login/")}\n\n'
                           f'Merci de votre confiance !\n'
                           f'Équipe Don Sang Plus',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[hospital.email],
                    fail_silently=True,
                )
                
                messages.success(request, f'✅ Hôpital {hospital.hospital_name} validé avec succès !')
                
            elif action == 'reject':
                hospital.verification_status = 'rejected'
                hospital.save()
                
                # Email de rejet
                send_mail(
                    subject='❌ Demande non validée - Don Sang Plus',
                    message=f'Bonjour {hospital.get_full_name()},\n\n'
                           f'Nous vous informons que votre demande d\'inscription pour '
                           f'{hospital.hospital_name} n\'a pas pu être validée.\n\n'
                           f'📧 Pour plus d\'informations, contactez-nous à :\n'
                           f'romualdndri9@gmail.com\n\n'
                           f'Cordialement,\n'
                           f'Équipe Don Sang Plus',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[hospital.email],
                    fail_silently=True,
                )
                
                messages.warning(request, f'❌ Hôpital {hospital.hospital_name} rejeté.')
                
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            print(f"Erreur validation hôpital: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    context = {'hospital': hospital}
    return render(request, 'admin/quick_validate.html', context)

# Vues supplémentaires pour la compatibilité
def LogoutView(request):
    """Vue de déconnexion alternative"""
    logout(request)
    return redirect('home')

def logout_default_user(request):
    """Déconnexion utilisateur par défaut"""
    if request.user.is_authenticated:
        logout(request)
    return redirect('accounts:login')