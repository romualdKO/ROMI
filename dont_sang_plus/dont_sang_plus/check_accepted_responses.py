#!/usr/bin/env python
"""
Vérifier pourquoi les 4 réponses acceptées de RO123_E ne sont pas complétées
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from django.contrib.auth import get_user_model
from donations.models import DonationResponse, BloodRequest

User = get_user_model()

print("=" * 100)
print("🔍 ANALYSE DES RÉPONSES ACCEPTÉES DE RO123_E")
print("=" * 100)
print()

try:
    donor = User.objects.get(username='RO123_E')
    print(f"👤 Donneur: {donor.get_full_name()} ({donor.username})")
    print(f"   Email: {donor.email}")
    print(f"   Groupe sanguin: {donor.blood_type}")
    print()
    
    # Récupérer toutes les réponses acceptées
    accepted_responses = DonationResponse.objects.filter(
        donor=donor,
        status='accepted'
    ).select_related('blood_request', 'blood_request__hospital')
    
    print(f"📊 Nombre de réponses acceptées: {accepted_responses.count()}")
    print()
    
    if accepted_responses.exists():
        print("=" * 100)
        print("DÉTAILS DES RÉPONSES ACCEPTÉES")
        print("=" * 100)
        
        for i, response in enumerate(accepted_responses, 1):
            print(f"\n{i}. RÉPONSE #{response.id}")
            print(f"   {'─' * 90}")
            print(f"   Date de réponse: {response.response_date}")
            print(f"   Statut de la réponse: {response.status.upper()}")
            print(f"   Message du donneur: {response.message[:100] if response.message else 'Aucun'}...")
            
            # Détails de la demande
            blood_request = response.blood_request
            print(f"\n   📋 DEMANDE DE SANG ASSOCIÉE:")
            print(f"      ID: {blood_request.id}")
            print(f"      Hôpital: {blood_request.hospital.hospital_name}")
            print(f"      Groupe sanguin demandé: {blood_request.blood_type}")
            print(f"      Quantité: {blood_request.quantity} poche(s)")
            print(f"      Date limite: {blood_request.deadline}")
            print(f"      Urgence: {blood_request.urgency}")
            print(f"      ⚠️  STATUT DE LA DEMANDE: {blood_request.status.upper()}")
            print(f"      is_fulfilled: {blood_request.is_fulfilled}")
            
            # Compter toutes les réponses pour cette demande
            all_responses_for_request = DonationResponse.objects.filter(
                blood_request=blood_request
            )
            print(f"\n   📊 Statistiques de la demande:")
            print(f"      Total réponses: {all_responses_for_request.count()}")
            print(f"      - Acceptées: {all_responses_for_request.filter(status='accepted').count()}")
            print(f"      - Complétées: {all_responses_for_request.filter(status='completed').count()}")
            print(f"      - En attente: {all_responses_for_request.filter(status='pending').count()}")
            print(f"      - Rejetées: {all_responses_for_request.filter(status='rejected').count()}")
            
            # Diagnostic
            print(f"\n   🔍 DIAGNOSTIC:")
            if blood_request.status == 'completed':
                print(f"      ✅ La demande est marquée 'completed'")
                print(f"      ❌ MAIS la réponse est toujours 'accepted' (PROBLÈME DE CASCADE!)")
            elif blood_request.status == 'approved':
                print(f"      ⚠️  La demande est 'approved' mais pas encore 'completed'")
                print(f"      → L'hôpital n'a pas encore marqué la demande comme 'Effectué'")
            elif blood_request.status == 'pending':
                print(f"      ⚠️  La demande est toujours 'pending'")
                print(f"      → L'hôpital n'a pas encore approuvé la demande")
            else:
                print(f"      ⚠️  Statut inhabituel: {blood_request.status}")
            
            print(f"\n   💡 ACTION REQUISE:")
            if blood_request.status != 'completed':
                print(f"      1. L'hôpital doit se connecter")
                print(f"      2. Aller dans 'Historique'")
                print(f"      3. Trouver la demande du {blood_request.deadline}")
                print(f"      4. Cliquer sur le dropdown 'Statut'")
                print(f"      5. Sélectionner 'Effectué'")
                print(f"      6. Le système mettra automatiquement à jour la réponse → 'completed'")
                print(f"      7. Le donneur sera verrouillé pour 90 jours")
            else:
                print(f"      ⚠️  PROBLÈME DE CODE: La demande est 'completed' mais la réponse ne l'est pas!")
                print(f"      → Le cascade n'a pas fonctionné, il faut investiguer update_request_status")
    
    print("\n" + "=" * 100)
    print("📋 RÉSUMÉ DU PROBLÈME")
    print("=" * 100)
    print()
    
    completed_requests = 0
    approved_requests = 0
    pending_requests = 0
    
    for response in accepted_responses:
        if response.blood_request.status == 'completed':
            completed_requests += 1
        elif response.blood_request.status == 'approved':
            approved_requests += 1
        elif response.blood_request.status == 'pending':
            pending_requests += 1
    
    print(f"Sur les {accepted_responses.count()} réponses acceptées:")
    print(f"  - {completed_requests} demande(s) marquée(s) 'completed' (CASCADE N'A PAS FONCTIONNÉ)")
    print(f"  - {approved_requests} demande(s) marquée(s) 'approved' (en attente de marquage 'Effectué')")
    print(f"  - {pending_requests} demande(s) encore 'pending' (pas encore approuvées)")
    print()
    
    if completed_requests > 0:
        print("⚠️  PROBLÈME CRITIQUE: Le système de cascade ne fonctionne pas!")
        print("   → Vérifier la vue update_request_status dans views.py")
        print()
    
    if approved_requests > 0 or pending_requests > 0:
        print("💡 SOLUTION: L'hôpital doit marquer les demandes comme 'Effectué'")
        print("   → Les réponses passeront automatiquement de 'accepted' à 'completed'")
        print("   → Le donneur sera verrouillé pour 90 jours")
        print()

except User.DoesNotExist:
    print("❌ Donneur RO123_E non trouvé dans la base de données")

print("=" * 100)
