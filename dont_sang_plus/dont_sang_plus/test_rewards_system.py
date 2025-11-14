"""
Script de test pour vérifier le système de récompenses
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from accounts.models import CustomUser
from donations.models import DonorRanking, HospitalBenefit, DonorVoucher

def test_rewards_system():
    """Tester le système de récompenses"""
    
    print("=" * 70)
    print("🧪 TEST DU SYSTÈME DE RÉCOMPENSES")
    print("=" * 70)
    
    # 1. Vérifier les donneurs
    print("\n📋 1. DONNEURS ENREGISTRÉS")
    print("-" * 70)
    donors = CustomUser.objects.filter(user_type='donor')
    if not donors.exists():
        print("❌ Aucun donneur trouvé.")
        return
    
    for donor in donors[:5]:  # Afficher les 5 premiers
        print(f"  👤 {donor.first_name} {donor.last_name} - {donor.blood_type or 'Groupe sanguin non défini'}")
    
    # 2. Vérifier les classements
    print(f"\n🏆 2. CLASSEMENTS DES DONNEURS")
    print("-" * 70)
    rankings = DonorRanking.objects.all().select_related('donor')
    
    if not rankings.exists():
        print("⚠️ Aucun classement créé. Les classements seront créés automatiquement après le premier don.")
    else:
        for ranking in rankings:
            tier_emoji = {
                'standard': '⭐',
                'bronze': '🥉',
                'silver': '🥈',
                'gold': '🥇',
                'platinum': '💎'
            }.get(ranking.current_tier, '⭐')
            
            print(f"  {tier_emoji} {ranking.donor.first_name} {ranking.donor.last_name}")
            print(f"     Niveau: {ranking.get_current_tier_display()}")
            print(f"     Dons: {ranking.total_donations} | Points: {ranking.points}")
            print(f"     Réduction: {ranking.get_discount_rate()}%")
            print()
    
    # 3. Vérifier les bénéfices hospitaliers
    print(f"🎁 3. BÉNÉFICES DISPONIBLES")
    print("-" * 70)
    benefits = HospitalBenefit.objects.filter(is_active=True).select_related('hospital')
    
    if not benefits.exists():
        print("❌ Aucun bénéfice créé. Exécutez 'python setup_benefits.py'")
    else:
        current_hospital = None
        for benefit in benefits:
            if current_hospital != benefit.hospital:
                current_hospital = benefit.hospital
                print(f"\n  🏥 {benefit.hospital.hospital_name}")
            
            tier_name = {
                'standard': 'STANDARD',
                'bronze': 'BRONZE',
                'silver': 'ARGENT',
                'gold': 'OR',
                'platinum': 'PLATINE'
            }.get(benefit.minimum_tier, benefit.minimum_tier.upper())
            
            print(f"     • {benefit.title} [{tier_name}] - {benefit.discount_percentage}%")
    
    # 4. Vérifier les bons de réduction
    print(f"\n🎫 4. BONS DE RÉDUCTION ÉMIS")
    print("-" * 70)
    vouchers = DonorVoucher.objects.all().select_related('donor', 'hospital')
    
    if not vouchers.exists():
        print("⚠️ Aucun bon émis. Les bons seront créés automatiquement quand un donneur")
        print("   atteint un nouveau niveau après un don.")
    else:
        for voucher in vouchers:
            status = "✅ Valide" if voucher.is_valid() else "❌ Expiré/Utilisé"
            print(f"  {status} | {voucher.voucher_code}")
            print(f"     Donneur: {voucher.donor.first_name} {voucher.donor.last_name}")
            print(f"     Hôpital: {voucher.hospital.hospital_name}")
            print(f"     Réduction: {voucher.discount_percentage}%")
            print(f"     Valide jusqu'au: {voucher.valid_until.strftime('%d/%m/%Y')}")
            print()
    
    # 5. Statistiques globales
    print(f"📊 5. STATISTIQUES GLOBALES")
    print("-" * 70)
    total_donors = donors.count()
    total_rankings = rankings.count()
    total_benefits = benefits.count()
    total_vouchers = vouchers.count()
    
    print(f"  👥 Total donneurs: {total_donors}")
    print(f"  🏆 Classements créés: {total_rankings}")
    print(f"  🎁 Bénéfices actifs: {total_benefits}")
    print(f"  🎫 Bons émis: {total_vouchers}")
    
    # Répartition par tier
    if rankings.exists():
        print(f"\n  📈 Répartition par niveau:")
        for tier, label in [
            ('standard', 'Standard ⭐'),
            ('bronze', 'Bronze 🥉'),
            ('silver', 'Argent 🥈'),
            ('gold', 'Or 🥇'),
            ('platinum', 'Platine 💎')
        ]:
            count = rankings.filter(current_tier=tier).count()
            if count > 0:
                percentage = (count / total_rankings) * 100
                print(f"     {label}: {count} ({percentage:.1f}%)")
    
    print("\n" + "=" * 70)
    print("✅ TEST TERMINÉ")
    print("=" * 70)
    print("\n💡 PROCHAINES ÉTAPES:")
    print("   1. Connectez-vous en tant que donneur")
    print("   2. Cliquez sur 'Mes Avantages' dans le menu")
    print("   3. Effectuez un don pour voir votre classement se mettre à jour")
    print("   4. Téléchargez votre bon de réduction en PDF")
    print()

if __name__ == '__main__':
    test_rewards_system()
