"""
Script pour simuler un don et vérifier le verrouillage automatique
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from accounts.models import CustomUser
from donations.models import BloodRequest, DonationResponse, DonorAvailability
from django.utils import timezone

def simulate_donation_lock():
    """Simuler un don et vérifier le verrouillage"""
    
    print("=" * 70)
    print("🧪 TEST DE VERROUILLAGE APRÈS DON")
    print("=" * 70)
    
    # Trouver un donneur
    donor = CustomUser.objects.filter(user_type='donor', blood_type__isnull=False).first()
    
    if not donor:
        print("❌ Aucun donneur avec groupe sanguin trouvé.")
        return
    
    print(f"\n👤 Donneur de test: {donor.first_name} {donor.last_name}")
    print(f"   Email: {donor.email}")
    print(f"   Groupe: {donor.blood_type}")
    
    # Vérifier la disponibilité AVANT
    availability, _ = DonorAvailability.objects.get_or_create(donor=donor)
    
    print(f"\n📊 ÉTAT AVANT DON:")
    print(f"   • is_available: {availability.is_available}")
    print(f"   • next_available_date: {availability.next_available_date or 'Non défini'}")
    
    # Simuler un don (marquer is_available = False et définir next_available_date)
    print(f"\n🩸 SIMULATION D'UN DON COMPLÉTÉ...")
    
    availability.is_available = False
    availability.next_available_date = timezone.now().date() + timezone.timedelta(days=90)
    availability.notes = f"🩸 Don simulé le {timezone.now().strftime('%d/%m/%Y')} pour test de verrouillage."
    availability.save()
    
    print(f"   ✅ Don simulé avec succès")
    
    # Vérifier la disponibilité APRÈS
    availability.refresh_from_db()
    
    print(f"\n📊 ÉTAT APRÈS DON:")
    print(f"   • is_available: {availability.is_available}")
    print(f"   • next_available_date: {availability.next_available_date}")
    print(f"   • Notes: {availability.notes}")
    
    # Calculer les jours restants
    if availability.next_available_date:
        days_remaining = (availability.next_available_date - timezone.now().date()).days
        print(f"   • Jours restants: {days_remaining} jours")
    
    # Vérifier si le donneur peut donner
    can_donate = True
    if not availability.is_available:
        can_donate = False
        print(f"\n❌ VERROUILLÉ: is_available = False")
    
    if availability.next_available_date and availability.next_available_date > timezone.now().date():
        can_donate = False
        print(f"❌ VERROUILLÉ: next_available_date dans le futur")
    
    if can_donate:
        print(f"\n⚠️  PROBLÈME: Le donneur peut encore donner !")
    else:
        print(f"\n✅ VERROUILLAGE ACTIF: Le donneur NE PEUT PAS donner")
    
    print("\n" + "=" * 70)
    print("🧪 TEST TERMINÉ")
    print("=" * 70)
    
    print("\n💡 ACTIONS À FAIRE:")
    print("   1. Allez sur http://127.0.0.1:8001/")
    print(f"   2. Connectez-vous avec: {donor.email}")
    print("   3. Le bouton 'Je veux donner' devrait être GRISÉ et DÉSACTIVÉ")
    print("   4. Un message d'alerte jaune devrait s'afficher en haut du dashboard")
    print(f"   5. Le message devrait dire: 'Vous ne pouvez pas donner avant le {availability.next_available_date.strftime('%d/%m/%Y')}'")
    
    print("\n🔧 POUR DÉBLOQUER LE DONNEUR (après test):")
    print("   1. Allez dans l'admin Django: http://127.0.0.1:8001/admin/")
    print("   2. Trouvez DonorAvailability pour ce donneur")
    print("   3. Cochez 'is_available' et supprimez 'next_available_date'")
    print("   OU utilisez ce script Python:")
    print(f"""
    from donations.models import DonorAvailability
    from accounts.models import CustomUser
    donor = CustomUser.objects.get(email='{donor.email}')
    availability = DonorAvailability.objects.get(donor=donor)
    availability.is_available = True
    availability.next_available_date = None
    availability.notes = "Débloqué pour test"
    availability.save()
    """)

if __name__ == '__main__':
    simulate_donation_lock()
