#!/usr/bin/env python
"""
Script pour réparer les réponses acceptées dont les demandes sont marquées completed
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from donations.models import DonationResponse, BloodRequest, DonorAvailability, DonorRanking, DonorVoucher, ChatMessage
import random, string

User = get_user_model()

print("=" * 100)
print("🔧 RÉPARATION DES RÉPONSES ACCEPTÉES AVEC DEMANDES COMPLETED")
print("=" * 100)
print()

# Trouver toutes les réponses acceptées dont la demande est completed
problematic_responses = DonationResponse.objects.filter(
    status='accepted',
    blood_request__status='completed'
).select_related('donor', 'blood_request', 'blood_request__hospital')

print(f"📊 Réponses à réparer: {problematic_responses.count()}")
print()

if problematic_responses.exists():
    print("Voulez-vous procéder à la réparation ? (oui/non)")
    confirmation = input("> ").strip().lower()
    
    if confirmation in ['oui', 'yes', 'o', 'y']:
        print()
        print("🔧 DÉBUT DE LA RÉPARATION")
        print("=" * 100)
        
        repaired_count = 0
        
        for response in problematic_responses:
            print(f"\n📝 Réparation de la réponse #{response.id}")
            print(f"   Donneur: {response.donor.get_full_name()} ({response.donor.username})")
            print(f"   Demande: #{response.blood_request.id} de {response.blood_request.hospital.hospital_name}")
            print(f"   Date de réponse: {response.response_date.date()}")
            
            # 1. Marquer la réponse comme complétée
            response.status = 'completed'
            response.save()
            print(f"   ✅ Statut mis à jour: accepted → completed")
            
            # 2. Verrouiller le donneur pour 90 jours à partir de la date de réponse
            availability, _ = DonorAvailability.objects.get_or_create(donor=response.donor)
            lock_date = response.response_date.date() + timezone.timedelta(days=90)
            
            availability.is_available = False
            availability.next_available_date = lock_date
            availability.notes = f"🩸 Don effectué le {response.response_date.strftime('%d/%m/%Y')} à {response.blood_request.hospital.hospital_name}. Pour votre santé, vous ne pouvez pas donner à nouveau avant 3 mois."
            availability.save()
            print(f"   🔒 Donneur verrouillé jusqu'au {lock_date.strftime('%d/%m/%Y')}")
            
            # Débloquer automatiquement si la date est passée
            if lock_date <= timezone.now().date():
                availability.auto_unlock()
                print(f"   🔓 Date passée → Donneur débloqué automatiquement")
            
            # 3. Mettre à jour le classement du donneur
            ranking, created = DonorRanking.objects.get_or_create(donor=response.donor)
            
            # Vérifier si ce don n'a pas déjà été compté
            if not created:
                # Compter les dons complétés actuels
                actual_completed = DonationResponse.objects.filter(
                    donor=response.donor,
                    status='completed'
                ).count()
                
                if ranking.total_donations < actual_completed:
                    ranking.total_donations = actual_completed
                    print(f"   📊 Dons comptabilisés: {ranking.total_donations}")
            else:
                ranking.total_donations = 1
                print(f"   📊 Premier don comptabilisé")
            
            ranking.last_donation_date = response.response_date.date()
            ranking.points = ranking.total_donations * 100
            old_tier = ranking.current_tier
            ranking.update_tier()
            ranking.save()
            print(f"   🏆 Niveau: {ranking.get_current_tier_display()} ({ranking.points} points)")
            
            # 4. Si changement de niveau, créer un bon de réduction
            if old_tier != ranking.current_tier:
                voucher_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                valid_until = timezone.now().date() + timezone.timedelta(days=365)
                
                DonorVoucher.objects.create(
                    donor=response.donor,
                    hospital=response.blood_request.hospital,
                    voucher_code=voucher_code,
                    discount_percentage=ranking.get_discount_rate(),
                    valid_until=valid_until
                )
                print(f"   🎟️  Bon créé: {voucher_code} ({ranking.get_discount_rate()}% de réduction)")
                
                # Message de félicitation
                ChatMessage.objects.create(
                    donation_response=response,
                    sender=response.blood_request.hospital,
                    message=f"🎊 FÉLICITATIONS ! Vous avez atteint le niveau {ranking.get_current_tier_display().upper()} ! "
                           f"Vous bénéficiez maintenant d'une réduction de {ranking.get_discount_rate()}% sur vos soins. "
                           f"Votre bon de réduction (code: {voucher_code}) est disponible dans 'Mes Avantages'.",
                    is_read=False
                )
                print(f"   💬 Message de félicitation envoyé")
            
            repaired_count += 1
        
        print()
        print("=" * 100)
        print(f"✅ RÉPARATION TERMINÉE: {repaired_count} réponse(s) réparée(s)")
        print("=" * 100)
        print()
        
        # Afficher le résumé par donneur
        print("📊 RÉSUMÉ PAR DONNEUR:")
        print("-" * 100)
        
        affected_donors = set(r.donor for r in problematic_responses)
        for donor in affected_donors:
            availability, _ = DonorAvailability.objects.get_or_create(donor=donor)
            ranking, _ = DonorRanking.objects.get_or_create(donor=donor)
            
            completed_count = DonationResponse.objects.filter(
                donor=donor,
                status='completed'
            ).count()
            
            print(f"\n👤 {donor.get_full_name()} ({donor.username})")
            print(f"   Dons complétés: {completed_count}")
            print(f"   Niveau: {ranking.get_current_tier_display()}")
            print(f"   Points: {ranking.points}")
            print(f"   Disponible: {'✅ Oui' if availability.is_currently_available() else f'❌ Non (jusqu\'au {availability.next_available_date})'}")
    else:
        print("❌ Réparation annulée")
else:
    print("✅ Aucune réponse à réparer !")

print()
print("=" * 100)
