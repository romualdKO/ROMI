"""
Script pour mettre à jour le statut d'une réponse de donation de 'pending' à 'completed'
"""
import os
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from donations.models import DonationResponse
from accounts.models import CustomUser

# Trouver le donneur roro_344 (KONAN N'DRI ROMUALD KONAN)
try:
    donor = CustomUser.objects.filter(username='roro_344').first()
    
    if not donor:
        print("❌ Donneur ROROCLINC non trouvé")
        print("\nDonneurs disponibles:")
        for user in CustomUser.objects.filter(user_type='donor'):
            print(f"  - {user.username} ({user.get_full_name()})")
    else:
        print(f"✅ Donneur trouvé: {donor.username} ({donor.get_full_name()})")
        
        # Trouver les réponses de ce donneur
        responses = DonationResponse.objects.filter(donor=donor)
        
        print(f"\n📋 Réponses de {donor.username}:")
        for response in responses:
            print(f"\n  ID: {response.id}")
            print(f"  Demande: {response.blood_request}")
            print(f"  Statut actuel: {response.status}")
            print(f"  Date: {response.response_date}")
            
        # Demander confirmation pour mettre à jour
        print("\n" + "="*60)
        print("MISE À JOUR DU STATUT")
        print("="*60)
        
        # Trouver les réponses en attente
        pending_responses = responses.filter(status='pending')
        
        if not pending_responses.exists():
            print("❌ Aucune réponse en attente trouvée")
        else:
            print(f"\n{pending_responses.count()} réponse(s) en attente trouvée(s):")
            
            for resp in pending_responses:
                resp.status = 'completed'
                resp.save()
                print(f"✅ Réponse #{resp.id} mise à jour: pending → completed")
                
        print("\n✅ Mise à jour terminée!")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
