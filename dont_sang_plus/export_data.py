import os
import django
import json
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from accounts.models import CustomUser
from donations.models import BloodRequest, DonationResponse, DonorAvailability

def export_users():
    """Exporter les utilisateurs"""
    users_data = []
    for user in CustomUser.objects.all():
        user_data = {
            'model': 'accounts.customuser',
            'fields': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_type': user.user_type,
                'phone_number': user.phone_number,
                'address': user.address,
                'city': user.city,
                'blood_type': user.blood_type,
                'birth_date': user.birth_date.isoformat() if user.birth_date else None,
                'hospital_name': user.hospital_name,
                'hospital_type': user.hospital_type,
                'is_verified': user.is_verified,
                'verification_status': user.verification_status,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.isoformat(),
            }
        }
        users_data.append(user_data)
    return users_data

def export_blood_requests():
    """Exporter les demandes de sang"""
    requests_data = []
    for request in BloodRequest.objects.all():
        request_data = {
            'model': 'donations.bloodrequest',
            'fields': {
                'hospital_id': request.hospital_id,
                'blood_type': request.blood_type,
                'quantity': request.quantity,
                'urgency': request.urgency,
                'description': request.description,
                'address': request.address,
                'city': request.city,
                'contact_info': request.contact_info,
                'created_at': request.created_at.isoformat(),
                'is_active': request.is_active,
            }
        }
        requests_data.append(request_data)
    return requests_data

def main():
    print("🔄 Export des données Don Sang Plus...")
    
    try:
        # Export des utilisateurs
        users = export_users()
        print(f"✅ {len(users)} utilisateurs exportés")
        
        # Export des demandes de sang
        requests = export_blood_requests()
        print(f"✅ {len(requests)} demandes de sang exportées")
        
        # Sauvegarder dans un fichier
        all_data = users + requests
        
        with open('don_sang_plus_backup.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Sauvegarde complète dans don_sang_plus_backup.json")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")

if __name__ == '__main__':
    main()