#!/usr/bin/env python
"""
Script de test pour vérifier les corrections de la logique de disponibilité
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from donations.models import DonorAvailability, DonationResponse

User = get_user_model()

print("=" * 80)
print("TEST DES CORRECTIONS DE LA LOGIQUE DE DISPONIBILITÉ")
print("=" * 80)
print()

# Test 1: Vérifier is_currently_available()
print("✅ TEST 1: Méthode is_currently_available()")
print("-" * 80)

donors = User.objects.filter(user_type='donor')
for donor in donors:
    availability, created = DonorAvailability.objects.get_or_create(donor=donor)
    
    print(f"\n👤 {donor.username}")
    print(f"   is_available: {availability.is_available}")
    print(f"   next_available_date: {availability.next_available_date}")
    print(f"   is_currently_available(): {availability.is_currently_available()}")
    
    # Test de cohérence
    today = timezone.now().date()
    expected = True
    
    if not availability.is_available:
        expected = False
    if availability.next_available_date and availability.next_available_date > today:
        expected = False
    
    if availability.is_currently_available() == expected:
        print(f"   ✅ COHÉRENT")
    else:
        print(f"   ❌ INCOHÉRENT! Attendu: {expected}, Obtenu: {availability.is_currently_available()}")

# Test 2: Vérifier auto_unlock()
print("\n\n✅ TEST 2: Méthode auto_unlock()")
print("-" * 80)

# Simuler un donneur avec date passée
test_donor = donors.first()
if test_donor:
    availability, _ = DonorAvailability.objects.get_or_create(donor=test_donor)
    
    # Sauvegarder l'état original
    original_is_available = availability.is_available
    original_next_date = availability.next_available_date
    
    # Cas 1: Date dans le passé
    print(f"\nCas 1: Date dans le passé")
    availability.is_available = False
    availability.next_available_date = timezone.now().date() - timedelta(days=1)
    availability.save()
    
    print(f"   Avant auto_unlock(): is_available={availability.is_available}, next_available_date={availability.next_available_date}")
    
    unlocked = availability.auto_unlock()
    availability.refresh_from_db()
    
    print(f"   Après auto_unlock(): is_available={availability.is_available}, next_available_date={availability.next_available_date}")
    print(f"   Retour de auto_unlock(): {unlocked}")
    
    if unlocked and availability.is_available and availability.next_available_date is None:
        print(f"   ✅ DÉBLOCAGE RÉUSSI")
    else:
        print(f"   ❌ ÉCHEC DU DÉBLOCAGE")
    
    # Cas 2: Date dans le futur
    print(f"\nCas 2: Date dans le futur")
    availability.is_available = False
    availability.next_available_date = timezone.now().date() + timedelta(days=30)
    availability.save()
    
    print(f"   Avant auto_unlock(): is_available={availability.is_available}, next_available_date={availability.next_available_date}")
    
    unlocked = availability.auto_unlock()
    availability.refresh_from_db()
    
    print(f"   Après auto_unlock(): is_available={availability.is_available}, next_available_date={availability.next_available_date}")
    print(f"   Retour de auto_unlock(): {unlocked}")
    
    if not unlocked and not availability.is_available:
        print(f"   ✅ PAS DE DÉBLOCAGE (CORRECT)")
    else:
        print(f"   ❌ DÉBLOCAGE INATTENDU")
    
    # Restaurer l'état original
    availability.is_available = original_is_available
    availability.next_available_date = original_next_date
    availability.save()
    print(f"\n   État original restauré")

# Test 3: Vérifier get_lock_reason()
print("\n\n✅ TEST 3: Méthode get_lock_reason()")
print("-" * 80)

for donor in donors:
    availability, _ = DonorAvailability.objects.get_or_create(donor=donor)
    reason = availability.get_lock_reason()
    
    print(f"\n👤 {donor.username}")
    print(f"   is_currently_available(): {availability.is_currently_available()}")
    print(f"   get_lock_reason(): {reason if reason else 'Aucune (disponible)'}")

# Test 4: Vérifier la cohérence avec les dons complétés
print("\n\n✅ TEST 4: Cohérence avec les dons complétés")
print("-" * 80)

for donor in donors:
    completed_responses = DonationResponse.objects.filter(donor=donor, status='completed')
    
    if completed_responses.exists():
        last_completed = completed_responses.order_by('-response_date').first()
        expected_lock_until = last_completed.response_date.date() + timedelta(days=90)
        
        print(f"\n👤 {donor.username}")
        print(f"   Dernier don complété: {last_completed.response_date.date()}")
        print(f"   Verrouillage attendu jusqu'au: {expected_lock_until}")
        
        availability, _ = DonorAvailability.objects.get_or_create(donor=donor)
        print(f"   is_available actuel: {availability.is_available}")
        print(f"   next_available_date actuel: {availability.next_available_date}")
        
        today = timezone.now().date()
        if expected_lock_until > today:
            # Le donneur devrait être verrouillé
            if not availability.is_available and availability.next_available_date == expected_lock_until:
                print(f"   ✅ COHÉRENT (verrouillé correctement)")
            else:
                print(f"   ⚠️  INCOHÉRENCE DÉTECTÉE")
                print(f"      Attendu: is_available=False, next_available_date={expected_lock_until}")
        else:
            # Le donneur devrait être disponible
            if availability.is_currently_available():
                print(f"   ✅ COHÉRENT (disponible correctement)")
            else:
                print(f"   ⚠️  INCOHÉRENCE: Le donneur devrait être disponible maintenant")

print("\n" + "=" * 80)
print("✅ TESTS TERMINÉS")
print("=" * 80)
print()
print("📋 RÉSUMÉ:")
print("- is_currently_available() : Logique unifiée de vérification")
print("- auto_unlock() : Déblocage automatique des donneurs")
print("- get_lock_reason() : Messages personnalisés pour les donneurs")
print("- Protection contre modification manuelle après don")
print()
