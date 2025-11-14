#!/usr/bin/env python
"""
Script de diagnostic complet de la logique de disponibilité des donneurs
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from django.contrib.auth import get_user_model
from donations.models import DonorAvailability, DonationResponse, BloodRequest

User = get_user_model()

print("=" * 80)
print("DIAGNOSTIC COMPLET DE LA LOGIQUE DE DISPONIBILITÉ DES DONNEURS")
print("=" * 80)
print()

# 1. VÉRIFIER TOUS LES DONNEURS
print("📊 1. ÉTAT DE TOUS LES DONNEURS")
print("-" * 80)
donors = User.objects.filter(user_type='donor')
print(f"Nombre total de donneurs: {donors.count()}")
print()

for donor in donors:
    print(f"\n👤 DONNEUR: {donor.username} ({donor.get_full_name()})")
    print(f"   Email: {donor.email}")
    print(f"   Groupe sanguin: {donor.blood_type}")
    
    # Vérifier la disponibilité
    try:
        availability = DonorAvailability.objects.get(donor=donor)
        print(f"   ✅ A un enregistrement DonorAvailability")
        print(f"      - is_available: {availability.is_available}")
        print(f"      - next_available_date: {availability.next_available_date}")
        
        # Logique de disponibilité actuelle
        today = date.today()
        is_really_available = True
        reason = []
        
        if not availability.is_available:
            is_really_available = False
            reason.append("is_available=False")
        
        if availability.next_available_date and availability.next_available_date > today:
            is_really_available = False
            days_remaining = (availability.next_available_date - today).days
            reason.append(f"next_available_date dans {days_remaining} jours")
        
        if is_really_available:
            print(f"      ✅ DISPONIBLE pour donner")
        else:
            print(f"      ❌ INDISPONIBLE: {', '.join(reason)}")
            
    except DonorAvailability.DoesNotExist:
        print(f"   ⚠️  AUCUN enregistrement DonorAvailability (PROBLÈME!)")
        print(f"      → Le donneur devrait être créé automatiquement")
    
    # Vérifier les réponses aux demandes
    all_responses = DonationResponse.objects.filter(donor=donor)
    print(f"   📝 Réponses aux demandes: {all_responses.count()}")
    
    if all_responses.exists():
        pending_count = all_responses.filter(status='pending').count()
        accepted_count = all_responses.filter(status='accepted').count()
        completed_count = all_responses.filter(status='completed').count()
        rejected_count = all_responses.filter(status='rejected').count()
        
        print(f"      - pending: {pending_count}")
        print(f"      - accepted: {accepted_count}")
        print(f"      - completed: {completed_count}")
        print(f"      - rejected: {rejected_count}")
        
        # Trouver la dernière réponse complétée
        last_completed = all_responses.filter(status='completed').order_by('-response_date').first()
        if last_completed:
            print(f"      - Dernier don complété: {last_completed.response_date.date()}")
            expected_lock_date = last_completed.response_date.date() + timedelta(days=90)
            print(f"      - Verrouillage attendu jusqu'au: {expected_lock_date}")
            
            # Vérifier la cohérence
            try:
                availability = DonorAvailability.objects.get(donor=donor)
                if availability.next_available_date != expected_lock_date:
                    print(f"      ⚠️  INCOHÉRENCE: next_available_date devrait être {expected_lock_date}")
                if availability.is_available:
                    print(f"      ⚠️  INCOHÉRENCE: is_available devrait être False")
            except DonorAvailability.DoesNotExist:
                pass

print("\n" + "=" * 80)
print("📋 2. PROBLÈMES DÉTECTÉS DANS LA LOGIQUE")
print("=" * 80)

problems = []

# Problème 1: Donneurs sans DonorAvailability
donors_without_availability = []
for donor in donors:
    if not DonorAvailability.objects.filter(donor=donor).exists():
        donors_without_availability.append(donor.username)

if donors_without_availability:
    problems.append({
        'titre': '❌ Donneurs sans enregistrement DonorAvailability',
        'description': f"{len(donors_without_availability)} donneur(s): {', '.join(donors_without_availability)}",
        'impact': 'Ces donneurs peuvent avoir des erreurs lors de la vérification de disponibilité',
        'solution': 'Créer automatiquement DonorAvailability pour chaque donneur'
    })

# Problème 2: Incohérence entre is_available et next_available_date
inconsistent_donors = []
for donor in donors:
    try:
        availability = DonorAvailability.objects.get(donor=donor)
        today = date.today()
        
        # Si next_available_date est dans le futur, is_available devrait être False
        if availability.next_available_date and availability.next_available_date > today:
            if availability.is_available:
                inconsistent_donors.append(f"{donor.username} (is_available=True mais next_available_date dans le futur)")
        
        # Si next_available_date est passé, is_available devrait être True
        elif availability.next_available_date and availability.next_available_date <= today:
            if not availability.is_available:
                inconsistent_donors.append(f"{donor.username} (is_available=False mais next_available_date passé)")
                
    except DonorAvailability.DoesNotExist:
        pass

if inconsistent_donors:
    problems.append({
        'titre': '❌ Incohérence entre is_available et next_available_date',
        'description': f"{len(inconsistent_donors)} donneur(s) avec incohérence",
        'details': inconsistent_donors,
        'impact': 'La logique de disponibilité est ambiguë',
        'solution': 'Synchroniser automatiquement is_available basé sur next_available_date'
    })

# Problème 3: Donneurs avec dons complétés mais disponibles
donors_completed_but_available = []
for donor in donors:
    completed_responses = DonationResponse.objects.filter(donor=donor, status='completed')
    if completed_responses.exists():
        last_completed = completed_responses.order_by('-response_date').first()
        expected_lock_until = last_completed.response_date.date() + timedelta(days=90)
        
        if expected_lock_until > date.today():
            # Le donneur devrait être verrouillé
            try:
                availability = DonorAvailability.objects.get(donor=donor)
                if availability.is_available or not availability.next_available_date or availability.next_available_date < expected_lock_until:
                    donors_completed_but_available.append(
                        f"{donor.username} (dernier don: {last_completed.response_date.date()}, "
                        f"devrait être verrouillé jusqu'au {expected_lock_until})"
                    )
            except DonorAvailability.DoesNotExist:
                pass

if donors_completed_but_available:
    problems.append({
        'titre': '❌ Donneurs avec dons récents mais marqués disponibles',
        'description': f"{len(donors_completed_but_available)} donneur(s) devraient être verrouillés",
        'details': donors_completed_but_available,
        'impact': 'CRITIQUE: Les donneurs peuvent donner avant les 90 jours',
        'solution': 'Recalculer les verrouillages basés sur les dons complétés'
    })

# Problème 4: Logique dans update_availability permet de contourner le verrouillage
problems.append({
    'titre': '⚠️  update_availability permet de modifier la disponibilité',
    'description': 'La vue update_availability vérifie seulement next_available_date',
    'impact': 'Un donneur verrouillé pourrait théoriquement modifier sa disponibilité manuellement',
    'solution': 'Empêcher toute modification manuelle si le donneur est verrouillé après un don'
})

# Problème 5: Pas de nettoyage automatique des verrouillages expirés
problems.append({
    'titre': '⚠️  Pas de déblocage automatique des donneurs',
    'description': 'Si next_available_date est passé, is_available reste False',
    'impact': 'Les donneurs peuvent rester bloqués même après les 90 jours',
    'solution': 'Ajouter une méthode pour débloquer automatiquement les donneurs'
})

# Afficher tous les problèmes
if problems:
    for i, problem in enumerate(problems, 1):
        print(f"\n{i}. {problem['titre']}")
        print(f"   Description: {problem['description']}")
        if 'details' in problem:
            for detail in problem['details']:
                print(f"      • {detail}")
        print(f"   Impact: {problem['impact']}")
        print(f"   Solution: {problem['solution']}")
else:
    print("\n✅ Aucun problème détecté!")

print("\n" + "=" * 80)
print("💡 3. RECOMMANDATIONS POUR AMÉLIORER LA LOGIQUE")
print("=" * 80)

recommendations = [
    {
        'titre': '1. Ajouter une méthode is_currently_available() dans DonorAvailability',
        'code': '''
def is_currently_available(self):
    """Vérifie si le donneur est vraiment disponible aujourd'hui"""
    from django.utils import timezone
    today = timezone.now().date()
    
    # Si explicitement indisponible
    if not self.is_available:
        return False
    
    # Si date de disponibilité dans le futur
    if self.next_available_date and self.next_available_date > today:
        return False
    
    return True
        '''
    },
    {
        'titre': '2. Ajouter une méthode auto_unlock() pour débloquer automatiquement',
        'code': '''
def auto_unlock(self):
    """Débloque automatiquement le donneur si la date est passée"""
    from django.utils import timezone
    today = timezone.now().date()
    
    if self.next_available_date and self.next_available_date <= today:
        self.is_available = True
        self.next_available_date = None
        self.save()
        return True
    return False
        '''
    },
    {
        'titre': '3. Appeler auto_unlock() dans donor_dashboard',
        'code': '''
# Dans donor_dashboard, avant la vérification
availability, created = DonorAvailability.objects.get_or_create(donor=request.user)
availability.auto_unlock()  # Débloquer si nécessaire
availability.refresh_from_db()

# Puis utiliser la méthode is_currently_available()
can_respond_to_requests = availability.is_currently_available()
        '''
    },
    {
        'titre': '4. Empêcher modification manuelle si verrouillé après don',
        'code': '''
# Dans update_availability
# Vérifier si le verrouillage vient d'un don complété
last_completed = DonationResponse.objects.filter(
    donor=request.user, status='completed'
).order_by('-response_date').first()

if last_completed:
    lock_until = last_completed.response_date.date() + timedelta(days=90)
    if lock_until > timezone.now().date():
        return JsonResponse({
            'error': f'Vous ne pouvez pas modifier votre disponibilité avant le {lock_until.strftime("%d/%m/%Y")} suite à votre dernier don.'
        }, status=403)
        '''
    },
    {
        'titre': '5. Utiliser une seule source de vérité',
        'code': '''
# RECOMMANDATION: Utiliser UNIQUEMENT next_available_date
# et calculer is_available dynamiquement via une property

@property
def is_available(self):
    from django.utils import timezone
    today = timezone.now().date()
    if self.next_available_date and self.next_available_date > today:
        return False
    return True
        '''
    }
]

for rec in recommendations:
    print(f"\n{rec['titre']}")
    print(f"{rec['code']}")

print("\n" + "=" * 80)
print("✅ DIAGNOSTIC TERMINÉ")
print("=" * 80)
