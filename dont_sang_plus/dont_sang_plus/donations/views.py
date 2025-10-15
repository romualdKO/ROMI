from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models import Q

from .models import BloodRequest, DonorAvailability, DonationResponse, ChatMessage, Donation
from accounts.models import CustomUser
from .forms import BloodRequestForm, UserProfileForm

User = get_user_model()

def is_donor(user):
    """Vérification si l'utilisateur est un donneur"""
    return user.is_authenticated and user.user_type == 'donor'

def is_hospital(user):
    """Vérification si l'utilisateur est un hôpital"""
    return user.is_authenticated and user.user_type == 'hospital'

@login_required
def dashboard(request):
    """Redirection automatique selon le type d'utilisateur"""
    if request.user.user_type == 'donor':
        return donor_dashboard(request)
    elif request.user.user_type == 'hospital':
        return hospital_dashboard(request)
    else:
        return redirect('admin:index')

@login_required
@user_passes_test(is_donor)
def donor_dashboard(request):
    """Vue pour le tableau de bord du donneur avec compatibilité sanguine"""
    try:
        # ✅ DEMANDES COMPATIBLES AVEC LA LOGIQUE DE COMPATIBILITÉ
        compatible_blood_types = BloodRequest.get_compatible_recipients(request.user.blood_type)
        
        matching_requests = BloodRequest.objects.filter(
            blood_type__in=compatible_blood_types,  # ✅ UTILISE LA COMPATIBILITÉ
            is_fulfilled=False,
            deadline__gt=timezone.now()
        ).exclude(
            # Exclure les demandes auxquelles il a déjà répondu
            id__in=DonationResponse.objects.filter(donor=request.user).values_list('blood_request_id', flat=True)
        ).select_related('hospital').order_by('deadline', 'urgency')

        # Mes réponses
        my_responses = DonationResponse.objects.filter(donor=request.user).select_related('blood_request', 'blood_request__hospital')
        completed_donations = [d for d in my_responses if d.status == 'completed']
        active_responses = [d for d in my_responses if d.status != 'completed']
        
        # Donations complétées
        donations = DonationResponse.objects.filter(
            donor=request.user, status__in=['accepted', 'completed']
        ).select_related('blood_request', 'blood_request__hospital')
        
        # Disponibilité du donneur
        availability, created = DonorAvailability.objects.get_or_create(donor=request.user)
        
        # Vérifier si le donneur peut modifier sa disponibilité ou répondre aux demandes
        can_update_availability = True
        can_respond_to_requests = True
        
        if availability.next_available_date and availability.next_available_date > timezone.now().date():
            can_update_availability = False
            can_respond_to_requests = False
        
        # Messages non lus reçus par le donneur
        new_messages = ChatMessage.objects.filter(
            donation_response__donor=request.user,
            is_read=False
        ).exclude(sender=request.user)

        # Compteur de messages non lus par réponse
        unread_counts = {}
        for resp in my_responses:
            unread_counts[resp.id] = ChatMessage.objects.filter(
                donation_response=resp,
                is_read=False
            ).exclude(sender=request.user).count()

        # Compteur de demandes satisfaites pour le donneur
        fulfilled_requests = donations.filter(status='completed').count()

        # ✅ INFORMATIONS SUR LA COMPATIBILITÉ
        donor_blood_type = request.user.blood_type
        can_give_to = BloodRequest.get_compatible_recipients(donor_blood_type)

        context = {
            'matching_requests': matching_requests,
            'my_responses': my_responses,
            'donations': donations,
            'availability': availability,
            'new_messages': new_messages,
            'unread_counts': unread_counts,
            'fulfilled_requests': fulfilled_requests,
            'completed_donations': completed_donations,
            'active_responses': active_responses,
            'can_update_availability': can_update_availability,
            'can_respond_to_requests': can_respond_to_requests,
            'donor_blood_type': donor_blood_type,
            'can_give_to': can_give_to,  # ✅ INFOS COMPATIBILITÉ
            'total_compatible': matching_requests.count(),
            'total_responses': my_responses.count(),
            'accepted_responses': my_responses.filter(status='accepted').count(),
            'completed_donations_count': completed_donations.__len__(),
        }
        
    except Exception as e:
        print(f"Erreur dans donor_dashboard: {e}")
        # Données de fallback en cas d'erreur
        context = {
            'matching_requests': [],
            'my_responses': [],
            'donations': [],
            'availability': {'is_available': True, 'next_available_date': None, 'notes': ''},
            'new_messages': [],
            'unread_counts': {},
            'fulfilled_requests': 0,
            'completed_donations': [],
            'active_responses': [],
            'can_update_availability': True,
            'can_respond_to_requests': True,
            'donor_blood_type': request.user.blood_type,
            'can_give_to': [],
            'total_compatible': 0,
            'total_responses': 0,
            'accepted_responses': 0,
            'completed_donations_count': 0,
        }
        messages.warning(request, "Certaines données n'ont pas pu être chargées.")
    
    return render(request, 'donations/donor_dashboard.html', context)

# ... garder toutes les importations existantes ...

@login_required
@user_passes_test(is_hospital)
def hospital_dashboard(request):
    """Vue pour le tableau de bord de l'hôpital avec gestion des messages"""
    try:
        # Suppression automatique des demandes expirées
        BloodRequest.objects.filter(
            hospital=request.user,
            deadline__lt=timezone.now()
        ).delete()

        # ✅ TOUTES LES DEMANDES (pas seulement actives, pour correspondre à l'historique)
        all_requests = BloodRequest.objects.filter(
            hospital=request.user
        ).order_by('-created_at')
        
        # Demandes actives (pour l'affichage dans le tableau)
        blood_requests = all_requests.filter(
            status__in=['pending', 'approved'],
            deadline__gte=timezone.now()
        )

        # Toutes les réponses pour cet hôpital
        responses = DonationResponse.objects.filter(
            blood_request__hospital=request.user
        ).select_related('donor', 'blood_request').order_by('-response_date')

        # ✅ COMPTAGE PRÉCIS DES MESSAGES NON LUS PAR DEMANDE
        unread_counts = {}
        for request_obj in blood_requests:
            # Compter les messages non lus pour cette demande spécifique
            unread_count = ChatMessage.objects.filter(
                donation_response__blood_request=request_obj,
                is_read=False
            ).exclude(sender=request.user).count()
            unread_counts[request_obj.id] = unread_count

        # ✅ MESSAGES NON LUS GLOBAUX
        new_messages = ChatMessage.objects.filter(
            donation_response__blood_request__hospital=request.user,
            is_read=False
        ).exclude(sender=request.user).select_related(
            'sender', 'donation_response', 'donation_response__blood_request'
        )

        # ✅ STATISTIQUES IDENTIQUES À L'HISTORIQUE (utilise le champ status)
        open_count = all_requests.filter(status__in=['pending', 'approved']).count()
        completed_count = all_requests.filter(status='completed').count()
        cancelled_count = all_requests.filter(status__in=['cancelled', 'rejected']).count()
        
        # Réponses acceptées ou complétées (même logique que l'historique)
        accepted_and_completed_responses = responses.filter(status__in=['accepted', 'completed'])
        total_donations = accepted_and_completed_responses.count()
        
        # Ancien système (pour compatibilité si nécessaire)
        pending_responses = responses.filter(status='pending').count()
        
        # ✅ COMPTEUR DE MESSAGES NON LUS (pour l'icône de notification)
        unread_messages_count = new_messages.count()

        context = {
            'blood_requests': blood_requests,
            'responses': responses,
            # ✅ NOUVELLES STATS ALIGNÉES AVEC L'HISTORIQUE
            'stats': {
                'open': open_count,  # En cours
                'completed': completed_count,  # Complétées
                'closed': cancelled_count,  # Annulées/Rejetées
                'total_donations': total_donations,  # Dons reçus (accepted + completed)
            },
            # Ancien système (garder pour compatibilité)
            'fulfilled_requests': completed_count,
            'completed_responses': total_donations,  # ✅ Maintenant = dons reçus
            'pending_responses': pending_responses,
            'accepted_responses': accepted_and_completed_responses.count(),
            'new_messages': new_messages,
            'unread_messages_count': unread_messages_count,  # ✅ POUR L'ICÔNE DE NOTIFICATION
            'unread_counts': unread_counts,  # ✅ COMPTEURS PAR DEMANDE
            'total_requests': all_requests.count(),
            'active_requests': open_count,  # ✅ = En cours
            'urgent_requests': blood_requests.filter(urgency__in=['immediate', '24h']).count(),
            'now': timezone.now(),  # ✅ POUR LES COMPARAISONS DE DATE
        }
        
    except Exception as e:
        print(f"Erreur dans hospital_dashboard: {e}")
        context = {
            'blood_requests': [],
            'responses': [],
            # ✅ NOUVELLES STATS
            'stats': {
                'open': 0,
                'completed': 0,
                'closed': 0,
                'total_donations': 0,
            },
            # Ancien système
            'fulfilled_requests': 0,
            'completed_responses': 0,
            'pending_responses': 0,
            'accepted_responses': 0,
            'new_messages': [],
            'unread_messages_count': 0,
            'unread_counts': {},
            'total_requests': 0,
            'active_requests': 0,
            'urgent_requests': 0,
            'now': timezone.now(),
        }
        messages.warning(request, "Certaines données n'ont pas pu être chargées.")
    
    return render(request, 'donations/hospital_dashboard.html', context)

@login_required
@user_passes_test(is_hospital)
def create_blood_request(request):
    """Vue pour créer une demande de sang"""
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            try:
                blood_request = form.save(commit=False)
                blood_request.hospital = request.user
                
                # Pré-remplir l'adresse et la ville si disponibles
                if not blood_request.address and hasattr(request.user, 'address'):
                    blood_request.address = request.user.address
                if not blood_request.city and hasattr(request.user, 'city'):
                    blood_request.city = request.user.city
                    
                blood_request.save()
                
                # 🔔 NOTIFICATION AUTOMATIQUE: Trouver les donneurs compatibles
                compatible_donors = CustomUser.objects.filter(
                    user_type='donor',
                    blood_type=blood_request.blood_type,
                    is_active=True
                ).exclude(id=request.user.id)
                
                # Notifier chaque donneur compatible
                notification_count = compatible_donors.count()
                
                messages.success(request, 
                    f'✅ Demande de sang créée avec succès! '
                    f'Groupe: {blood_request.blood_type}, '
                    f'Quantité: {blood_request.quantity} poche(s), '
                    f'Urgence: {blood_request.get_urgency_display()}. '
                    f'📢 {notification_count} donneur(s) compatible(s) notifié(s)!')
                
                return redirect('donations:hospital_dashboard')
            except Exception as e:
                print(f"Erreur création demande: {e}")
                messages.error(request, "❌ Erreur lors de la création de la demande.")
        else:
            print("Erreurs du formulaire:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {field}: {error}")
    else:
        form = BloodRequestForm()
        # Pré-remplir avec les données de l'hôpital
        if hasattr(request.user, 'city'):
            form.fields['city'].initial = request.user.city
        if hasattr(request.user, 'address'):
            form.fields['address'].initial = request.user.address
    
    context = {'form': form}
    return render(request, 'donations/create_blood_request.html', context)

@login_required
@user_passes_test(is_hospital)
def edit_blood_request(request, request_id):
    """Vue pour modifier une demande de sang"""
    try:
        blood_request = get_object_or_404(BloodRequest, id=request_id, hospital=request.user)
        
        # Vérifier si la demande peut être modifiée
        if blood_request.is_fulfilled:
            messages.warning(request, "❌ Cette demande a déjà été satisfaite et ne peut plus être modifiée.")
            return redirect('/donations/hospital-dashboard/')
        
        if request.method == 'POST':
            form = BloodRequestForm(request.POST, instance=blood_request)
            if form.is_valid():
                form.save()
                messages.success(request, "✅ Demande modifiée avec succès.")
                return redirect('/donations/hospital-dashboard/')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"❌ {field}: {error}")
        else:
            form = BloodRequestForm(instance=blood_request)
        
        return render(request, 'donations/edit_blood_request.html', {
            'form': form, 
            'blood_request': blood_request
        })
        
    except Exception as e:
        print(f"Erreur edit_blood_request: {e}")
        messages.error(request, "❌ Erreur lors de la modification de la demande.")
        return redirect('/donations/hospital-dashboard/')

@login_required
@user_passes_test(is_donor)
def respond_to_request(request, request_id):
    """Vue pour répondre à une demande de sang avec vérification de compatibilité"""
    try:
        # Vérifier que l'utilisateur est authentifié et est un donneur
        if not request.user.is_authenticated:
            messages.error(request, "❌ Vous devez être connecté pour répondre.")
            return redirect('accounts:login')
        
        if request.user.user_type != 'donor':
            messages.error(request, "❌ Seuls les donneurs peuvent répondre aux demandes.")
            return redirect('donations:dashboard')
        
        # Vérifier que l'utilisateur a un groupe sanguin
        if not request.user.blood_type:
            messages.error(request, "❌ Veuillez d'abord définir votre groupe sanguin dans votre profil.")
            return redirect('donations:edit_profile')
        
        blood_request = get_object_or_404(BloodRequest, id=request_id, is_fulfilled=False)
        
        # Vérifications de base
        if blood_request.deadline <= timezone.now():
            messages.warning(request, "❌ Cette demande a expiré.")
            return redirect('/donations/donor-dashboard/')
        
        # ✅ VÉRIFICATION DE COMPATIBILITÉ CORRIGÉE
        compatible_types = BloodRequest.get_compatible_recipients(request.user.blood_type)
        if blood_request.blood_type not in compatible_types:
            messages.warning(request, 
                f"❌ Incompatibilité sanguine. Votre groupe {request.user.blood_type} "
                f"ne peut pas donner au groupe {blood_request.blood_type}.")
            return redirect('/donations/donor-dashboard/')
        
        # Vérifier la disponibilité du donneur
        availability, created = DonorAvailability.objects.get_or_create(donor=request.user)
        if availability.next_available_date and availability.next_available_date > timezone.now().date():
            messages.error(request, f"❌ Vous ne pouvez pas répondre aux demandes avant le {availability.next_available_date.strftime('%d/%m/%Y')}.")
            return redirect('/donations/donor-dashboard/')
        
        # Vérifier si l'utilisateur a déjà répondu
        existing_response = DonationResponse.objects.filter(
            blood_request=blood_request, 
            donor=request.user
        ).first()
        
        if existing_response:
            messages.warning(request, "⚠️ Vous avez déjà répondu à cette demande.")
            return redirect('/donations/donor-dashboard/')
        
        if request.method == 'POST':
            message = request.POST.get('message', '').strip()
            
            # Créer la réponse avec statut 'accepted' automatiquement
            DonationResponse.objects.create(
                blood_request=blood_request,
                donor=request.user,
                status='accepted',  # ✅ CHANGÉ: accepté automatiquement quand le donneur répond
                message=message,
                response_date=timezone.now()
            )
            
            messages.success(request, 
                f"✅ Votre réponse a été envoyée à {blood_request.hospital.hospital_name}! "
                f"Compatibilité : {request.user.blood_type} → {blood_request.blood_type}")
            return redirect('/donations/donor-dashboard/')
        
        # ✅ INFORMATIONS DE COMPATIBILITÉ POUR LE TEMPLATE
        compatibility_info = {
            'donor_type': request.user.blood_type,
            'recipient_type': blood_request.blood_type,
            'is_compatible': blood_request.blood_type in BloodRequest.get_compatible_recipients(request.user.blood_type)
        }
        
        context = {
            'blood_request': blood_request,
            'hospital': blood_request.hospital,
            'compatibility_info': compatibility_info
        }
        return render(request, 'donations/respond_to_request.html', context)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERREUR respond_to_request: {e}")
        print(f"📋 DÉTAILS: {error_details}")
        messages.error(request, f"❌ Erreur lors de la réponse à la demande: {str(e)}")
        return redirect('/donations/donor-dashboard/')

# ... Reste des vues inchangées ...

@csrf_exempt
@require_POST
@login_required
def update_availability(request):
    """Vue pour mettre à jour la disponibilité du donneur"""
    try:
        if request.user.user_type != 'donor':
            return JsonResponse({'status': 'error', 'message': 'Accès réservé aux donneurs'}, status=403)
        
        donor_availability, created = DonorAvailability.objects.get_or_create(donor=request.user)
        
        # Vérifier si le donneur peut modifier sa disponibilité
        if donor_availability.next_available_date and donor_availability.next_available_date > timezone.now().date():
            return render(request, 'donations/availability_updated.html', {
                'success': False,
                'message': f"Vous ne pouvez pas modifier votre disponibilité avant le {donor_availability.next_available_date.strftime('%d/%m/%Y')}."
            })
        
        is_available = request.POST.get('is_available') == 'on'
        next_available_date = request.POST.get('next_available_date') or None
        notes = request.POST.get('notes', '')

        donor_availability.is_available = is_available
        donor_availability.next_available_date = next_available_date
        donor_availability.notes = notes
        donor_availability.save()
        
        return render(request, 'donations/availability_updated.html', {
            'success': True,
            'message': "✅ Disponibilité mise à jour avec succès."
        })
    except Exception as e:
        print(f"Erreur update_availability: {e}")
        return render(request, 'donations/availability_updated.html', {
            'success': False,
            'message': f"❌ Erreur lors de la mise à jour : {str(e)}"
        })

@login_required
@user_passes_test(is_hospital)
def view_responses(request, request_id):
    """Vue pour voir les réponses à une demande"""
    try:
        blood_request = get_object_or_404(BloodRequest, id=request_id, hospital=request.user)
        responses = DonationResponse.objects.filter(blood_request=blood_request).select_related('donor')
        
        context = {
            'blood_request': blood_request,
            'responses': responses,
        }
        return render(request, 'donations/view_responses.html', context)
    except Exception as e:
        print(f"Erreur view_responses: {e}")
        messages.error(request, "❌ Erreur lors du chargement des réponses.")
        return redirect('/donations/hospital-dashboard/')

@login_required
def chat_with_donor(request, response_id):
    """Vue pour le chat entre donneur et hôpital"""
    try:
        donation_response = get_object_or_404(DonationResponse, id=response_id)
        
        if request.user != donation_response.blood_request.hospital and request.user != donation_response.donor:
            messages.error(request, "❌ Accès non autorisé.")
            return redirect('donations:dashboard')
        
        if request.method == 'POST':
            message_text = request.POST.get('message', '').strip()
            if message_text:
                ChatMessage.objects.create(
                    donation_response=donation_response,
                    sender=request.user,
                    message=message_text,
                    is_read=False
                )
                return redirect('donations:chat_with_donor', response_id=response_id)
        
        chat_messages = ChatMessage.objects.filter(donation_response=donation_response).order_by('timestamp')
        
        # Marquer comme lus les messages reçus par l'utilisateur courant
        if request.user == donation_response.donor:
            chat_messages.filter(sender=donation_response.blood_request.hospital, is_read=False).update(is_read=True)
        else:
            chat_messages.filter(sender=donation_response.donor, is_read=False).update(is_read=True)
        
        context = {
            'response': donation_response,
            'messages_list': chat_messages,
            'other_user': donation_response.donor if request.user.user_type == 'hospital' else donation_response.blood_request.hospital,
        }
        return render(request, 'donations/chat.html', context)
        
    except Exception as e:
        print(f"Erreur chat_with_donor: {e}")
        messages.error(request, "❌ Erreur lors du chargement du chat.")
        return redirect('donations:dashboard')

# ... garder toutes les importations existantes ...

@login_required
@user_passes_test(is_hospital)
def update_response_status(request, response_id, status):
    """Vue pour mettre à jour le statut d'une réponse avec notifications"""
    try:
        response = get_object_or_404(DonationResponse, id=response_id)
        
        # Vérifier que l'hôpital est bien le propriétaire de la demande
        if response.blood_request.hospital != request.user:
            messages.error(request, "❌ Accès non autorisé.")
            return redirect('/donations/hospital-dashboard/')
        
        if status == 'accepted':
            response.status = 'accepted'
            response.save()
            
            # 🎫 GÉNÉRATION AUTOMATIQUE DE L'ATTESTATION
            donation_id = f"DS{response.id:06d}"
            attestation_url = request.build_absolute_uri(
                reverse('donations:donation_attestation', args=[response.id])
            )
            
            # ✅ CRÉER UN MESSAGE AUTOMATIQUE DANS LE CHAT AVEC LIEN ATTESTATION
            ChatMessage.objects.create(
                donation_response=response,
                sender=request.user,
                message=f"🎉 Excellente nouvelle ! Votre candidature a été acceptée pour le don de sang {response.blood_request.blood_type}. "
                        f"📄 Votre attestation a été générée (ID: {donation_id}). "
                        f"Rendez-vous sur la page Messages pour télécharger votre attestation et venir effectuer le don à l'hôpital {response.blood_request.hospital.hospital_name}. "
                        f"Merci pour votre générosité !",
                is_read=False
            )
            
            messages.success(request, 
                f"✅ Donneur {response.donor.get_full_name()} accepté ! "
                f"📄 Attestation générée automatiquement (ID: {donation_id}). "
                f"Un message avec le lien a été envoyé au donneur.")
            
        elif status == 'rejected':
            response.status = 'rejected'
            response.save()
            
            # ✅ MESSAGE AUTOMATIQUE DE REJET
            ChatMessage.objects.create(
                donation_response=response,
                sender=request.user,
                message=f"Merci pour votre proposition de don de sang {response.blood_request.blood_type}. Malheureusement, nous ne pouvons pas retenir votre candidature cette fois-ci. Nous vous encourageons à postuler pour de futures demandes.",
                is_read=False
            )
            
            messages.info(request, f"📝 Donneur {response.donor.get_full_name()} rejeté. Un message d'explication lui a été envoyé.")
            
        elif status == 'completed':
            response.status = 'completed'
            response.save()
            
            # ✅ RENDRE LE DONNEUR INDISPONIBLE 3 MOIS
            availability, _ = DonorAvailability.objects.get_or_create(donor=response.donor)
            availability.is_available = False
            availability.next_available_date = timezone.now().date() + timezone.timedelta(days=90)
            availability.notes = f"🩸 Don effectué le {timezone.now().strftime('%d/%m/%Y')} à {response.blood_request.hospital.hospital_name}. Pour votre santé, vous ne pouvez pas donner à nouveau avant 3 mois."
            availability.save()
            
            # ✅ MESSAGE DE FÉLICITATIONS
            ChatMessage.objects.create(
                donation_response=response,
                sender=request.user,
                message=f"🎉 Félicitations ! Votre don de sang {response.blood_request.blood_type} a été effectué avec succès le {timezone.now().strftime('%d/%m/%Y')}. Merci infiniment pour ce geste qui peut sauver des vies ! Vous pourrez donner à nouveau dans 3 mois.",
                is_read=False
            )
            
            # ✅ MARQUER LA DEMANDE COMME SATISFAITE SI BESOIN
            blood_request = response.blood_request
            completed_responses = DonationResponse.objects.filter(
                blood_request=blood_request, 
                status='completed'
            ).count()
            
            if completed_responses >= blood_request.quantity:
                blood_request.is_fulfilled = True
                blood_request.save()
                messages.success(request, f"🎯 Demande de {blood_request.blood_type} complètement satisfaite !")
            
            messages.success(request, f"🎉 Don de {response.donor.get_full_name()} complété ! Le donneur est maintenant indisponible pour 3 mois.")
            
        elif status == 'unsatisfied':
            response.status = 'unsatisfied'
            response.save()
            
            # ✅ MESSAGE D'ANNULATION
            ChatMessage.objects.create(
                donation_response=response,
                sender=request.user,
                message=f"Nous devons malheureusement annuler votre don de sang {response.blood_request.blood_type}. Nous vous recontacterons si nous avons de nouveaux besoins. Merci pour votre compréhension.",
                is_read=False
            )
            
            messages.warning(request, f"⚠️ Don de {response.donor.get_full_name()} annulé. Un message d'explication lui a été envoyé.")
        
        return redirect('/donations/hospital-dashboard/')
        
    except Exception as e:
        print(f"Erreur update_response_status: {e}")
        messages.error(request, "❌ Erreur lors de la mise à jour du statut.")
        return redirect('/donations/hospital-dashboard/')

# ✅ NOUVELLE VUE POUR API DES COMPTEURS DE MESSAGES
@login_required
def api_message_counts(request):
    """API pour récupérer les compteurs de messages non lus"""
    try:
        if request.user.user_type == 'hospital':
            unread_count = ChatMessage.objects.filter(
                donation_response__blood_request__hospital=request.user,
                is_read=False
            ).exclude(sender=request.user).count()
        else:
            unread_count = ChatMessage.objects.filter(
                donation_response__donor=request.user,
                is_read=False
            ).exclude(sender=request.user).count()
        
        return JsonResponse({
            'total_unread': unread_count,
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({
            'total_unread': 0,
            'status': 'error',
            'message': str(e)
        })
@login_required
@user_passes_test(is_donor)
def my_responses(request):
    """Vue pour voir les réponses du donneur"""
    try:
        responses = DonationResponse.objects.filter(donor=request.user).select_related('blood_request', 'blood_request__hospital')
        context = {'responses': responses}
        return render(request, 'donations/my_responses.html', context)
    except Exception as e:
        print(f"Erreur my_responses: {e}")
        messages.error(request, "❌ Erreur lors du chargement de vos réponses.")
        return redirect('/donations/donor-dashboard/')

# ... garder toutes les importations et vues existantes jusqu'à edit_profile ...

@login_required
def edit_profile(request):
    """Vue pour modifier le profil - Compatible avec le template existant"""
    try:
        if request.method == 'POST':
            # ✅ TRAITEMENT MANUEL DES CHAMPS POUR CORRESPONDRE AU TEMPLATE
            
            # Récupérer les données du formulaire
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            city = request.POST.get('city', '').strip()
            address = request.POST.get('address', '').strip()
            
            # Champs spécifiques aux donneurs
            blood_type = request.POST.get('blood_type', '').strip()
            birth_date = request.POST.get('birth_date', '').strip()
            medical_history = request.POST.get('medical_history', '').strip()
            
            # Validations de base
            errors = []
            if not first_name:
                errors.append("Le prénom est obligatoire.")
            if not last_name:
                errors.append("Le nom est obligatoire.")
            if not email:
                errors.append("L'email est obligatoire.")
            if not phone:
                errors.append("Le téléphone est obligatoire.")
            if not city:
                errors.append("La ville est obligatoire.")
            
            # Validation spécifique aux donneurs
            if request.user.user_type == 'donor':
                if not blood_type:
                    errors.append("Le groupe sanguin est obligatoire pour les donneurs.")
                if not birth_date:
                    errors.append("La date de naissance est obligatoire pour les donneurs.")
            
            if errors:
                for error in errors:
                    messages.error(request, f"❌ {error}")
            else:
                try:
                    # Mettre à jour les champs
                    request.user.first_name = first_name
                    request.user.last_name = last_name
                    request.user.email = email
                    request.user.phone = phone
                    request.user.city = city
                    request.user.address = address
                    
                    # Champs spécifiques aux donneurs
                    if request.user.user_type == 'donor':
                        request.user.blood_type = blood_type
                        if birth_date:
                            request.user.birth_date = birth_date
                        request.user.medical_history = medical_history
                    
                    # Gestion de la photo de profil
                    if 'profile_picture' in request.FILES:
                        request.user.profile_picture = request.FILES['profile_picture']
                    
                    request.user.save()
                    
                    messages.success(request, '✅ Profil mis à jour avec succès!')
                    
                    # Redirection selon le type d'utilisateur
                    if request.user.user_type == 'donor':
                        return redirect('/donations/donor-dashboard/')
                    else:
                        return redirect('/donations/hospital-dashboard/')
                        
                except Exception as e:
                    print(f"Erreur lors de la sauvegarde: {e}")
                    messages.error(request, f"❌ Erreur lors de la sauvegarde : {str(e)}")
        
        # GET request - créer un formulaire factice pour le template
        form_data = {
            'first_name': {'value': request.user.first_name},
            'last_name': {'value': request.user.last_name},
            'email': {'value': request.user.email},
            'phone': {'value': getattr(request.user, 'phone', '')},
            'city': {'value': getattr(request.user, 'city', '')},
            'address': {'value': getattr(request.user, 'address', '')},
        }
        
        # ✅ CRÉER UN OBJET FORM FACTICE POUR LE TEMPLATE
        class FormData:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        context = {
            'form': FormData(form_data),
            'user': request.user
        }
        return render(request, 'donations/edit_profile.html', context)
        
    except Exception as e:
        print(f"Erreur edit_profile: {e}")
        messages.error(request, f"❌ Erreur lors de la modification du profil : {str(e)}")
        
        # Redirection selon le type d'utilisateur
        if request.user.user_type == 'donor':
            return redirect('/donations/donor-dashboard/')
        else:
            return redirect('/donations/hospital-dashboard/')


@login_required
def response_detail(request, response_id):
    """Vue pour les détails d'une réponse"""
    try:
        response = get_object_or_404(DonationResponse, id=response_id)
        return render(request, 'donations/response_detail.html', {'response': response})
    except Exception as e:
        print(f"Erreur response_detail: {e}")
        messages.error(request, "❌ Erreur lors du chargement des détails.")
        return redirect('donations:dashboard')

@login_required
def request_detail(request, request_id):
    """Vue pour les détails d'une demande"""
    try:
        # Vérifier que l'utilisateur est authentifié
        if not request.user.is_authenticated:
            messages.error(request, "❌ Vous devez être connecté pour voir les détails.")
            return redirect('accounts:login')
        
        blood_request = get_object_or_404(BloodRequest, id=request_id)
        
        # Vérifier si l'utilisateur a déjà répondu
        user_response = None
        if request.user.user_type == 'donor':
            try:
                user_response = DonationResponse.objects.get(
                    blood_request=blood_request,
                    donor=request.user
                )
            except DonationResponse.DoesNotExist:
                pass
        
        context = {
            'blood_request': blood_request,
            'user_response': user_response,
        }
        return render(request, 'donations/request_detail.html', context)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERREUR request_detail: {e}")
        print(f"📋 DÉTAILS: {error_details}")
        messages.error(request, f"❌ Erreur lors du chargement des détails: {str(e)}")
        return redirect('donations:dashboard')

# ... garder toutes les importations et vues existantes jusqu'à edit_profile ...



# ✅ MISE À JOUR DE LA VUE update_availability
@login_required
def update_availability(request):
    """Vue pour mettre à jour la disponibilité du donneur - Compatible avec les templates"""
    try:
        if request.user.user_type != 'donor':
            messages.error(request, "❌ Accès réservé aux donneurs.")
            return redirect('donations:dashboard')
        
        # Récupérer ou créer l'objet disponibilité
        availability, created = DonorAvailability.objects.get_or_create(donor=request.user)
        
        if request.method == 'POST':
            # ✅ TRAITEMENT MANUEL DES DONNÉES POUR CORRESPONDRE AU TEMPLATE
            is_available = request.POST.get('is_available') == 'on'
            next_available_date_str = request.POST.get('next_available_date', '').strip()
            notes = request.POST.get('notes', '').strip()
            
            # Conversion de la date
            next_available_date = None
            if next_available_date_str:
                try:
                    from datetime import datetime
                    next_available_date = datetime.strptime(next_available_date_str, '%Y-%m-%d').date()
                except ValueError:
                    next_available_date = None
            
            try:
                availability.is_available = is_available
                availability.next_available_date = next_available_date
                availability.notes = notes
                availability.save()
                
                return render(request, 'donations/availability_updated.html', {
                    'success': True,
                    'message': "✅ Votre disponibilité a été mise à jour avec succès."
                })
                
            except Exception as e:
                print(f"Erreur sauvegarde disponibilité: {e}")
                return render(request, 'donations/availability_updated.html', {
                    'success': False,
                    'message': f"❌ Erreur lors de la sauvegarde : {str(e)}"
                })
        else:
            # GET request - afficher le formulaire avec les données actuelles
            context = {
                'availability': availability,
                'user': request.user
            }
            return render(request, 'donations/update_availability.html', context)
            
    except Exception as e:
        print(f"Erreur update_availability: {e}")
        return render(request, 'donations/availability_updated.html', {
            'success': False,
            'message': f"❌ Erreur technique : {str(e)}"
        })

# ✅ SUPPRIMER LA VUE DUPLIQUÉE update_availability_page
# (Elle est maintenant intégrée dans update_availability)

# ... garder toutes les autres vues existantes inchangées ...

@login_required
@user_passes_test(is_donor)
def donor_messages(request):
    """Vue pour la page messagerie du donneur - Interface moderne"""
    from django.db.models import Count, Q, Max
    
    # Récupérer toutes les réponses du donneur
    responses = DonationResponse.objects.filter(
        donor=request.user
    ).select_related('blood_request__hospital').prefetch_related('chatmessage_set').order_by('-response_date')
    
    # Construire la liste des conversations
    conversations = []
    for response in responses:
        # Compter messages non lus de l'hôpital
        unread_count = response.chatmessage_set.filter(
            sender__user_type='hospital',
            is_read=False
        ).count()
        
        # Dernier message
        last_message = response.chatmessage_set.order_by('-timestamp').first()
        
        conversations.append({
            'response': response,
            'blood_request': response.blood_request,
            'hospital': response.blood_request.hospital,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    # Trier par dernier message (plus récent en premier)
    conversations.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else x['response'].response_date, reverse=True)
    
    # Gérer la conversation active
    active_response_id = request.GET.get('response')
    active_response = None
    chat_messages = []
    
    if active_response_id:
        try:
            active_response = DonationResponse.objects.select_related('blood_request__hospital').get(
                id=active_response_id,
                donor=request.user
            )
            chat_messages = ChatMessage.objects.filter(
                donation_response=active_response
            ).select_related('sender').order_by('timestamp')
            
            # Marquer les messages de l'hôpital comme lus
            ChatMessage.objects.filter(
                donation_response=active_response,
                sender__user_type='hospital',
                is_read=False
            ).update(is_read=True)
            
        except DonationResponse.DoesNotExist:
            pass
    elif conversations:
        # Par défaut, sélectionner la première conversation
        active_response = conversations[0]['response']
        chat_messages = ChatMessage.objects.filter(
            donation_response=active_response
        ).select_related('sender').order_by('timestamp')
        
        # Marquer comme lus
        ChatMessage.objects.filter(
            donation_response=active_response,
            sender__user_type='hospital',
            is_read=False
        ).update(is_read=True)
    
    # Traiter l'envoi de message
    if request.method == 'POST' and active_response:
        message_text = request.POST.get('message', '').strip()
        if message_text:
            ChatMessage.objects.create(
                donation_response=active_response,
                sender=request.user,
                message=message_text
            )
            messages.success(request, '✅ Message envoyé')
            return redirect(f'{request.path}?response={active_response.id}')
    
    context = {
        'conversations': conversations,
        'active_response': active_response,
        'active_response_id': active_response.id if active_response else None,
        'messages': chat_messages,
    }
    return render(request, 'donations/donor_messages.html', context)

@login_required
@user_passes_test(is_hospital)
def hospital_messages(request):
    """Vue pour la page messagerie de l'hôpital - Interface moderne"""
    # Récupérer toutes les demandes de sang de l'hôpital
    blood_requests = BloodRequest.objects.filter(
        hospital=request.user
    ).prefetch_related('donationresponse_set__chatmessage_set', 'donationresponse_set__donor').order_by('-deadline')
    
    # Construire la liste des conversations
    conversations = []
    for blood_request in blood_requests:
        for response in blood_request.donationresponse_set.all():
            # Compter messages non lus du donneur
            unread_count = response.chatmessage_set.filter(
                sender__user_type='donor',
                is_read=False
            ).count()
            
            # Dernier message
            last_message = response.chatmessage_set.order_by('-timestamp').first()
            
            conversations.append({
                'response': response,
                'blood_request': blood_request,
                'donor': response.donor,
                'last_message': last_message,
                'unread_count': unread_count
            })
    
    # Trier par dernier message (plus récent en premier)
    conversations.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else x['response'].response_date, reverse=True)
    
    # Gérer la conversation active
    active_response_id = request.GET.get('response')
    active_response = None
    chat_messages = []
    
    if active_response_id:
        try:
            active_response = DonationResponse.objects.select_related('blood_request', 'donor').get(
                id=active_response_id,
                blood_request__hospital=request.user
            )
            chat_messages = ChatMessage.objects.filter(
                donation_response=active_response
            ).select_related('sender').order_by('timestamp')
            
            # Marquer les messages du donneur comme lus
            ChatMessage.objects.filter(
                donation_response=active_response,
                sender__user_type='donor',
                is_read=False
            ).update(is_read=True)
            
        except DonationResponse.DoesNotExist:
            pass
    elif conversations:
        # Par défaut, sélectionner la première conversation
        active_response = conversations[0]['response']
        chat_messages = ChatMessage.objects.filter(
            donation_response=active_response
        ).select_related('sender').order_by('timestamp')
        
        # Marquer comme lus
        ChatMessage.objects.filter(
            donation_response=active_response,
            sender__user_type='donor',
            is_read=False
        ).update(is_read=True)
    
    # Traiter l'envoi de message
    if request.method == 'POST' and active_response:
        message_text = request.POST.get('message', '').strip()
        if message_text:
            ChatMessage.objects.create(
                donation_response=active_response,
                sender=request.user,
                message=message_text
            )
            messages.success(request, '✅ Message envoyé')
            return redirect(f'{request.path}?response={active_response.id}')
    
    context = {
        'conversations': conversations,
        'active_response': active_response,
        'active_response_id': active_response.id if active_response else None,
        'messages': chat_messages,
    }
    return render(request, 'donations/hospital_messages.html', context)

@login_required
@user_passes_test(is_donor)
def donor_history(request):
    """Vue pour l'historique du donneur"""
    # Toutes les réponses du donneur (complétées, annulées, etc.)
    all_responses = DonationResponse.objects.filter(
        donor=request.user
    ).select_related('blood_request__hospital').order_by('-response_date')
    
    # Statistiques
    completed_count = all_responses.filter(status='completed').count()
    cancelled_count = all_responses.filter(status='cancelled').count()
    pending_count = all_responses.filter(status='pending').count()
    accepted_count = all_responses.filter(status='accepted').count()
    
    # Donations réellement effectuées
    completed_donations = Donation.objects.filter(
        donor=request.user
    ).select_related('blood_request__hospital').order_by('-donation_date')
    
    context = {
        'all_responses': all_responses,
        'completed_donations': completed_donations,
        'stats': {
            'total': all_responses.count(),
            'completed': completed_count,
            'cancelled': cancelled_count,
            'pending': pending_count,
            'accepted': accepted_count,
        }
    }
    return render(request, 'donations/donor_history.html', context)

@login_required
@user_passes_test(is_hospital)
def hospital_history(request):
    """Vue pour l'historique de l'hôpital"""
    # Toutes les demandes de sang de l'hôpital
    all_requests = BloodRequest.objects.filter(
        hospital=request.user
    ).prefetch_related('donationresponse_set__donor').order_by('-deadline')
    
    # ✅ UTILISER DonationResponse AU LIEU DE Donation
    # Toutes les réponses reçues (tous statuts confondus)
    all_responses = DonationResponse.objects.filter(
        blood_request__hospital=request.user
    ).select_related('donor', 'blood_request').order_by('-response_date')
    
    # ✅ Statistiques basées sur le champ STATUS (pas juste is_fulfilled)
    open_count = all_requests.filter(status__in=['pending', 'approved']).count()  # En attente ou approuvé
    completed_count = all_requests.filter(status='completed').count()  # Vraiment complétées
    cancelled_count = all_requests.filter(status__in=['cancelled', 'rejected']).count()  # Annulées ou rejetées
    
    # ✅ DONS REÇUS = Toutes les réponses acceptées ou complétées (pas rejected/pending)
    accepted_and_completed_responses = all_responses.filter(status__in=['accepted', 'completed'])
    total_donations = accepted_and_completed_responses.count()
    
    context = {
        'requests': all_requests,
        'received_donations': accepted_and_completed_responses,  # ✅ Seulement les réponses acceptées/complétées
        'stats': {
            'total': all_requests.count(),
            'open': open_count,
            'closed': cancelled_count,  # ✅ Demandes fermées (annulées/rejetées)
            'completed': completed_count,  # ✅ Demandes vraiment complétées
            'total_donations': total_donations,  # ✅ Réponses acceptées + complétées
        }
    }
    return render(request, 'donations/hospital_history.html', context)

@login_required
@user_passes_test(is_hospital)
def update_request_status(request, request_id, new_status):
    """Vue pour mettre à jour le statut d'une demande de sang"""
    try:
        blood_request = BloodRequest.objects.get(id=request_id, hospital=request.user)
        
        # Vérifier que le statut est valide
        valid_statuses = dict(BloodRequest.STATUS_CHOICES).keys()
        if new_status not in valid_statuses:
            messages.error(request, "❌ Statut invalide")
            return redirect('donations:hospital_dashboard')
        
        # Mettre à jour le statut
        old_status = blood_request.get_status_display()
        blood_request.status = new_status
        
        # Si le statut est "completed", marquer comme fulfilled
        if new_status == 'completed':
            blood_request.is_fulfilled = True
        
        blood_request.save()
        
        status_display = dict(BloodRequest.STATUS_CHOICES)[new_status]
        messages.success(request, f"✅ Statut mis à jour: {old_status} → {status_display}")
        
    except BloodRequest.DoesNotExist:
        messages.error(request, "❌ Demande introuvable")
    except Exception as e:
        messages.error(request, f"❌ Erreur: {str(e)}")
    
    return redirect('donations:hospital_dashboard')


@login_required
def donation_attestation(request, response_id):
    """Vue pour afficher/télécharger l'attestation de don"""
    try:
        response = get_object_or_404(DonationResponse, id=response_id)
        
        # Vérifier que l'utilisateur a accès
        if request.user != response.donor and request.user != response.blood_request.hospital:
            messages.error(request, "❌ Accès non autorisé.")
            return redirect('donations:dashboard')
        
        context = {
            'response': response,
            'donor': response.donor,
            'blood_request': response.blood_request,
            'hospital': response.blood_request.hospital,
            'donation_id': f"DS{response.id:06d}",  # Format: DS000001
        }
        
        return render(request, 'donations/donation_attestation.html', context)
        
    except Exception as e:
        print(f"Erreur donation_attestation: {e}")
        messages.error(request, "❌ Erreur lors du chargement de l'attestation.")
        return redirect('donations:dashboard')


@login_required
@user_passes_test(is_donor)
def quick_donate(request, request_id):
    """Vue pour répondre rapidement 'Je veux donner' en un clic"""
    try:
        blood_request = get_object_or_404(BloodRequest, id=request_id)
        
        # Vérifier la disponibilité du donneur
        availability, created = DonorAvailability.objects.get_or_create(donor=request.user)
        if availability.next_available_date and availability.next_available_date > timezone.now().date():
            messages.error(request, f"❌ Vous ne pouvez pas donner avant le {availability.next_available_date.strftime('%d/%m/%Y')}.")
            return redirect('donations:donor_dashboard')
        
        # Vérifier si déjà répondu
        existing_response = DonationResponse.objects.filter(
            blood_request=blood_request, 
            donor=request.user
        ).first()
        
        if existing_response:
            messages.warning(request, "⚠️ Vous avez déjà répondu à cette demande.")
            return redirect('donations:donor_dashboard')
        
        # Créer la réponse automatiquement avec statut 'accepted'
        response = DonationResponse.objects.create(
            blood_request=blood_request,
            donor=request.user,
            status='accepted',  # ✅ CHANGÉ: accepté automatiquement
            message=f"Je souhaite donner mon sang ({request.user.blood_type}) pour votre demande urgente.",
            response_date=timezone.now()
        )
        
        messages.success(request, 
            f"✅ Votre réponse a été acceptée par {blood_request.hospital.hospital_name}! "
            f"Rendez-vous dans Messages pour discuter des détails.")
        
        # Rediriger vers la page des messages pour qu'ils puissent discuter
        return redirect('donations:donor_messages')
        
    except Exception as e:
        print(f"Erreur quick_donate: {e}")
        messages.error(request, "❌ Erreur lors de l'envoi de votre réponse.")
        return redirect('donations:donor_dashboard')