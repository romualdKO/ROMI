# Script de Diagnostic Automatique - Don Sang Plus
# Ce script vérifie la configuration et identifie les problèmes

import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from accounts.models import CustomUser
from donations.models import BloodRequest, DonationResponse, DonorAvailability
from django.utils import timezone

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_users():
    print_section("1. VÉRIFICATION DES UTILISATEURS")
    
    total_users = CustomUser.objects.count()
    donors = CustomUser.objects.filter(user_type='donor').count()
    hospitals = CustomUser.objects.filter(user_type='hospital').count()
    
    print(f"✅ Total utilisateurs : {total_users}")
    print(f"✅ Donneurs : {donors}")
    print(f"✅ Hôpitaux : {hospitals}")
    
    # Vérifier les donneurs sans groupe sanguin
    donors_no_blood_type = CustomUser.objects.filter(
        user_type='donor',
        blood_type__isnull=True
    ).count()
    
    if donors_no_blood_type > 0:
        print(f"\n⚠️  ATTENTION : {donors_no_blood_type} donneur(s) sans groupe sanguin !")
        print("   Ces utilisateurs ne peuvent pas répondre aux demandes.")
        
        # Liste des donneurs problématiques
        problematic_donors = CustomUser.objects.filter(
            user_type='donor',
            blood_type__isnull=True
        )
        
        for donor in problematic_donors:
            print(f"   - {donor.email} (ID: {donor.id})")
    else:
        print("✅ Tous les donneurs ont un groupe sanguin")

def check_requests():
    print_section("2. VÉRIFICATION DES DEMANDES DE SANG")
    
    total_requests = BloodRequest.objects.count()
    active_requests = BloodRequest.objects.filter(
        is_fulfilled=False,
        deadline__gt=timezone.now()
    ).count()
    expired_requests = BloodRequest.objects.filter(
        deadline__lte=timezone.now()
    ).count()
    
    print(f"✅ Total demandes : {total_requests}")
    print(f"✅ Demandes actives : {active_requests}")
    print(f"⚠️  Demandes expirées : {expired_requests}")
    
    # Vérifier les demandes sans hôpital
    requests_no_hospital = BloodRequest.objects.filter(
        hospital__isnull=True
    ).count()
    
    if requests_no_hospital > 0:
        print(f"\n🔴 ERREUR : {requests_no_hospital} demande(s) sans hôpital associé !")
    else:
        print("✅ Toutes les demandes ont un hôpital")

def check_responses():
    print_section("3. VÉRIFICATION DES RÉPONSES")
    
    total_responses = DonationResponse.objects.count()
    pending = DonationResponse.objects.filter(status='pending').count()
    accepted = DonationResponse.objects.filter(status='accepted').count()
    
    print(f"✅ Total réponses : {total_responses}")
    print(f"⏳ En attente : {pending}")
    print(f"✅ Acceptées : {accepted}")

def check_templates():
    print_section("4. VÉRIFICATION DES TEMPLATES")
    
    templates_dir = 'donations/templates/donations'
    required_templates = [
        'donor_dashboard.html',
        'request_detail.html',
        'respond_to_request.html',
        'hospital_dashboard.html'
    ]
    
    missing_templates = []
    for template in required_templates:
        path = os.path.join(templates_dir, template)
        if os.path.exists(path):
            print(f"✅ {template}")
        else:
            print(f"🔴 {template} - MANQUANT")
            missing_templates.append(template)
    
    if missing_templates:
        print(f"\n🔴 ERREUR : {len(missing_templates)} template(s) manquant(s)")
    else:
        print("\n✅ Tous les templates requis sont présents")

def check_urls():
    print_section("5. VÉRIFICATION DES URLS")
    
    from django.urls import reverse
    from django.urls.exceptions import NoReverseMatch
    
    urls_to_check = [
        ('donations:donor_dashboard', []),
        ('donations:hospital_dashboard', []),
        ('donations:respond_to_request', [1]),
        ('donations:request_detail', [1]),
        ('donations:edit_profile', []),
    ]
    
    for url_name, args in urls_to_check:
        try:
            url = reverse(url_name, args=args)
            print(f"✅ {url_name} → {url}")
        except NoReverseMatch:
            print(f"🔴 {url_name} - ERREUR: URL non trouvée")

def check_blood_compatibility():
    print_section("6. VÉRIFICATION DE LA COMPATIBILITÉ SANGUINE")
    
    # Tester la fonction de compatibilité
    try:
        compatible = BloodRequest.get_compatible_recipients('O+')
        print(f"✅ Fonction de compatibilité fonctionne")
        print(f"   O+ peut donner à : {', '.join(compatible)}")
    except Exception as e:
        print(f"🔴 ERREUR dans la fonction de compatibilité : {e}")

def main():
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         DIAGNOSTIC AUTOMATIQUE - DON SANG PLUS            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    try:
        check_users()
        check_requests()
        check_responses()
        check_templates()
        check_urls()
        check_blood_compatibility()
        
        print_section("RÉSUMÉ")
        print("✅ Diagnostic terminé avec succès")
        print("\n📋 Si des erreurs sont affichées ci-dessus, corrigez-les.")
        print("📋 Sinon, le problème vient probablement d'un utilisateur spécifique.")
        print("\n💡 Actions recommandées :")
        print("   1. Vérifier votre profil utilisateur")
        print("   2. S'assurer d'avoir un groupe sanguin défini")
        print("   3. Tester avec un compte différent")
        
    except Exception as e:
        print(f"\n🔴 ERREUR CRITIQUE : {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
