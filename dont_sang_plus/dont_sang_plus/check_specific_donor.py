"""
Vérifier et verrouiller un donneur spécifique
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from accounts.models import CustomUser
from donations.models import DonorAvailability, DonationResponse
from django.utils import timezone

# Trouver le donneur spécifique
donor = CustomUser.objects.get(email='romualdk059@gmail.com')

print("=" * 70)
print(f"👤 Donneur: {donor.first_name} {donor.last_name}")
print(f"   Email: {donor.email}")
print(f"   Groupe sanguin: {donor.blood_type}")
print("=" * 70)

# Vérifier la disponibilité
availability, created = DonorAvailability.objects.get_or_create(donor=donor)

print(f"\n📊 ÉTAT ACTUEL DE LA DISPONIBILITÉ:")
print(f"   • is_available: {availability.is_available}")
print(f"   • next_available_date: {availability.next_available_date or 'Non défini'}")
if availability.notes:
    print(f"   • Notes: {availability.notes}")

# Vérifier les dons complétés
completed_donations = DonationResponse.objects.filter(
    donor=donor,
    status='completed'
).count()

print(f"\n🩸 Dons complétés: {completed_donations}")

# Vérifier les réponses
all_responses = DonationResponse.objects.filter(donor=donor)
print(f"\n📋 HISTORIQUE DES RÉPONSES:")
for response in all_responses:
    print(f"   • Status: {response.status}")
    print(f"     Hôpital: {response.blood_request.hospital.hospital_name}")
    print(f"     Date: {response.response_date.strftime('%d/%m/%Y %H:%M')}")
    print(f"     Groupe: {response.blood_request.blood_type}")

# Si le donneur a fait un don complété, il devrait être verrouillé
if completed_donations > 0:
    last_completed = DonationResponse.objects.filter(
        donor=donor,
        status='completed'
    ).order_by('-response_date').first()
    
    print(f"\n⚠️  PROBLÈME DÉTECTÉ:")
    print(f"   Le donneur a {completed_donations} don(s) complété(s)")
    print(f"   Dernier don: {last_completed.response_date.strftime('%d/%m/%Y %H:%M')}")
    print(f"   MAIS is_available = {availability.is_available}")
    
    if availability.is_available:
        print(f"\n🔧 CORRECTION AUTOMATIQUE...")
        availability.is_available = False
        availability.next_available_date = last_completed.response_date.date() + timezone.timedelta(days=90)
        availability.notes = f"🩸 Don effectué le {last_completed.response_date.strftime('%d/%m/%Y')} à {last_completed.blood_request.hospital.hospital_name}. Pour votre santé, vous ne pouvez pas donner à nouveau avant 3 mois."
        availability.save()
        
        print(f"   ✅ Donneur verrouillé jusqu'au {availability.next_available_date.strftime('%d/%m/%Y')}")
    else:
        print(f"   ✅ Donneur déjà correctement verrouillé")
else:
    print(f"\n✅ Aucun don complété - Le donneur devrait être disponible")
    if not availability.is_available:
        print(f"⚠️  MAIS le donneur est marqué comme indisponible")
        print(f"   Raison possible: Verrouillé manuellement")

print("\n" + "=" * 70)
