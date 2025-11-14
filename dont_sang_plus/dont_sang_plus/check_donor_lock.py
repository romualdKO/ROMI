"""
Script pour vérifier et déboguer le verrouillage des donneurs après don
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from accounts.models import CustomUser
from donations.models import DonorAvailability, DonationResponse
from django.utils import timezone

def check_donor_lock():
    """Vérifier l'état de verrouillage des donneurs"""
    
    print("=" * 70)
    print("🔒 VÉRIFICATION DU VERROUILLAGE DES DONNEURS")
    print("=" * 70)
    
    # Récupérer tous les donneurs
    donors = CustomUser.objects.filter(user_type='donor')
    
    if not donors.exists():
        print("❌ Aucun donneur trouvé.")
        return
    
    print(f"\n📋 Total de donneurs: {donors.count()}\n")
    
    for donor in donors:
        print(f"👤 {donor.first_name} {donor.last_name} ({donor.blood_type or 'Pas de groupe sanguin'})")
        print(f"   Email: {donor.email}")
        
        # Vérifier la disponibilité
        try:
            availability = DonorAvailability.objects.get(donor=donor)
            
            print(f"   🔓 Disponibilité:")
            print(f"      • is_available: {availability.is_available}")
            print(f"      • next_available_date: {availability.next_available_date or 'Non défini'}")
            
            if availability.next_available_date:
                days_remaining = (availability.next_available_date - timezone.now().date()).days
                if days_remaining > 0:
                    print(f"      • Jours restants: {days_remaining} jours")
                    print(f"      • 🔒 VERROUILLÉ jusqu'au {availability.next_available_date.strftime('%d/%m/%Y')}")
                else:
                    print(f"      • ✅ Date passée, devrait être disponible")
            
            if availability.notes:
                print(f"      • Notes: {availability.notes[:80]}...")
            
            # Vérifier les dons complétés
            completed_donations = DonationResponse.objects.filter(
                donor=donor, 
                status='completed'
            ).count()
            print(f"   🩸 Dons complétés: {completed_donations}")
            
            # Dernier don
            last_donation = DonationResponse.objects.filter(
                donor=donor, 
                status='completed'
            ).order_by('-response_date').first()
            
            if last_donation:
                print(f"   📅 Dernier don: {last_donation.response_date.strftime('%d/%m/%Y %H:%M')}")
                print(f"      Hôpital: {last_donation.blood_request.hospital.hospital_name}")
            
            # Déterminer si le donneur peut donner
            can_donate = True
            reasons = []
            
            if not availability.is_available:
                can_donate = False
                reasons.append("Marqué comme indisponible")
            
            if availability.next_available_date and availability.next_available_date > timezone.now().date():
                can_donate = False
                reasons.append(f"Date de prochaine disponibilité: {availability.next_available_date.strftime('%d/%m/%Y')}")
            
            if can_donate:
                print(f"   ✅ PEUT DONNER")
            else:
                print(f"   ❌ NE PEUT PAS DONNER - Raisons: {', '.join(reasons)}")
            
        except DonorAvailability.DoesNotExist:
            print(f"   ⚠️  Pas d'enregistrement de disponibilité (sera créé à la première interaction)")
        
        print("-" * 70)
    
    # Résumé
    print("\n📊 RÉSUMÉ:")
    
    locked_donors = 0
    available_donors = 0
    
    for donor in donors:
        try:
            availability = DonorAvailability.objects.get(donor=donor)
            if not availability.is_available or (availability.next_available_date and availability.next_available_date > timezone.now().date()):
                locked_donors += 1
            else:
                available_donors += 1
        except DonorAvailability.DoesNotExist:
            available_donors += 1  # Considéré comme disponible par défaut
    
    print(f"   🔒 Donneurs verrouillés: {locked_donors}")
    print(f"   ✅ Donneurs disponibles: {available_donors}")
    
    print("\n" + "=" * 70)
    print("✅ VÉRIFICATION TERMINÉE")
    print("=" * 70)
    
    print("\n💡 CONSEILS:")
    print("   • Si un donneur est verrouillé à tort, allez dans l'admin Django")
    print("   • Modifiez l'objet DonorAvailability du donneur")
    print("   • Cochez 'is_available' et supprimez 'next_available_date'")
    print("   • Si un donneur devrait être verrouillé mais ne l'est pas,")
    print("     vérifiez que le don a bien été marqué comme 'completed'")
    print()

if __name__ == '__main__':
    check_donor_lock()
