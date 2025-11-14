"""
Script pour initialiser les bénéfices hospitaliers du système de récompenses
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from accounts.models import CustomUser
from donations.models import HospitalBenefit

def setup_benefits():
    """Créer des bénéfices pour tous les hôpitaux"""
    
    # Récupérer tous les hôpitaux
    hospitals = CustomUser.objects.filter(user_type='hospital')
    
    if not hospitals.exists():
        print("❌ Aucun hôpital trouvé dans la base de données.")
        print("💡 Créez d'abord un compte hôpital via l'interface d'inscription.")
        return
    
    benefits_created = 0
    
    for hospital in hospitals:
        print(f"\n🏥 Configuration des bénéfices pour : {hospital.hospital_name}")
        
        # Bénéfices standards pour tous les niveaux
        benefits_data = [
            {
                'title': '🩺 Consultation gratuite',
                'description': 'Bénéficiez d\'une consultation médicale gratuite dans notre établissement',
                'minimum_tier': 'bronze',
                'discount_percentage': 5
            },
            {
                'title': '💊 Réduction sur les médicaments',
                'description': 'Profitez d\'une réduction sur l\'achat de médicaments prescrits',
                'minimum_tier': 'bronze',
                'discount_percentage': 5
            },
            {
                'title': '🔬 Analyses médicales réduites',
                'description': 'Réduction sur les analyses et examens de laboratoire',
                'minimum_tier': 'silver',
                'discount_percentage': 10
            },
            {
                'title': '🏥 Hospitalisation prioritaire',
                'description': 'Accès prioritaire pour les hospitalisations non urgentes',
                'minimum_tier': 'silver',
                'discount_percentage': 10
            },
            {
                'title': '🩹 Soins infirmiers gratuits',
                'description': 'Bénéficiez de soins infirmiers à domicile sans frais',
                'minimum_tier': 'gold',
                'discount_percentage': 15
            },
            {
                'title': '🚑 Ambulance gratuite',
                'description': 'Service d\'ambulance gratuit en cas d\'urgence',
                'minimum_tier': 'gold',
                'discount_percentage': 15
            },
            {
                'title': '👨‍⚕️ Consultation spécialisée gratuite',
                'description': 'Consultation gratuite avec nos médecins spécialistes',
                'minimum_tier': 'platinum',
                'discount_percentage': 20
            },
            {
                'title': '🏨 Chambre VIP',
                'description': 'Accès gratuit aux chambres VIP lors de vos hospitalisations',
                'minimum_tier': 'platinum',
                'discount_percentage': 20
            },
        ]
        
        for benefit_data in benefits_data:
            # Créer ou mettre à jour le bénéfice
            benefit, created = HospitalBenefit.objects.get_or_create(
                hospital=hospital,
                title=benefit_data['title'],
                defaults={
                    'description': benefit_data['description'],
                    'minimum_tier': benefit_data['minimum_tier'],
                    'discount_percentage': benefit_data['discount_percentage'],
                    'is_active': True
                }
            )
            
            if created:
                print(f"  ✅ {benefit_data['title']} (Niveau: {benefit_data['minimum_tier'].upper()})")
                benefits_created += 1
            else:
                # Mettre à jour si existe déjà
                benefit.description = benefit_data['description']
                benefit.minimum_tier = benefit_data['minimum_tier']
                benefit.discount_percentage = benefit_data['discount_percentage']
                benefit.is_active = True
                benefit.save()
                print(f"  ♻️ {benefit_data['title']} (mis à jour)")
    
    print(f"\n✨ Configuration terminée !")
    print(f"📊 Total de nouveaux bénéfices créés : {benefits_created}")
    print(f"🏥 Hôpitaux configurés : {hospitals.count()}")
    print(f"\n💡 Les donneurs peuvent maintenant voir leurs avantages sur la page 'Mes Avantages'")

if __name__ == '__main__':
    print("=" * 60)
    print("🎁 INITIALISATION DES BÉNÉFICES HOSPITALIERS")
    print("=" * 60)
    setup_benefits()
