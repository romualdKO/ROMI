#!/usr/bin/env python
"""
Script pour nettoyer les emails en double avant d'appliquer la contrainte d'unicité
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from accounts.models import CustomUser
from django.db.models import Count

def find_duplicate_emails():
    """Trouve les emails en double"""
    print("🔍 Recherche des emails en double...")
    
    # Trouver les emails qui apparaissent plus d'une fois
    duplicates = CustomUser.objects.values('email').annotate(
        count=Count('email')
    ).filter(count__gt=1)
    
    print(f"📧 Emails en double trouvés : {duplicates.count()}")
    
    for duplicate in duplicates:
        email = duplicate['email']
        count = duplicate['count']
        print(f"  - {email} : {count} occurrences")
        
        # Afficher tous les utilisateurs avec cet email
        users = CustomUser.objects.filter(email=email)
        for i, user in enumerate(users):
            print(f"    {i+1}. ID: {user.id}, Username: {user.username}, Type: {user.user_type}")
    
    return duplicates

def fix_duplicate_emails():
    """Répare les emails en double"""
    print("\n🔧 Correction des emails en double...")
    
    duplicates = CustomUser.objects.values('email').annotate(
        count=Count('email')
    ).filter(count__gt=1)
    
    for duplicate in duplicates:
        email = duplicate['email']
        users = list(CustomUser.objects.filter(email=email).order_by('id'))
        
        print(f"\n📧 Traitement de l'email : {email}")
        
        # Garder le premier utilisateur tel quel
        first_user = users[0]
        print(f"  ✅ Conservé : {first_user.username} (ID: {first_user.id})")
        
        # Modifier les emails des autres utilisateurs
        for i, user in enumerate(users[1:], 1):
            # Créer un nouvel email unique
            base_email = email.split('@')[0]
            domain = email.split('@')[1]
            new_email = f"{base_email}_{user.id}@{domain}"
            
            # Vérifier que le nouvel email n'existe pas déjà
            counter = 1
            while CustomUser.objects.filter(email=new_email).exists():
                new_email = f"{base_email}_{user.id}_{counter}@{domain}"
                counter += 1
            
            user.email = new_email
            user.save()
            
            print(f"  🔄 Modifié : {user.username} (ID: {user.id}) -> {new_email}")

def main():
    print("🩸 NETTOYAGE DES EMAILS EN DOUBLE - Don Sang Plus")
    print("=" * 50)
    
    # Vérifier s'il y a des emails en double
    duplicates = find_duplicate_emails()
    
    if duplicates.count() == 0:
        print("✅ Aucun email en double trouvé !")
        return
    
    # Demander confirmation
    print(f"\n⚠️  {duplicates.count()} email(s) en double trouvé(s).")
    print("Les utilisateurs en double recevront un nouvel email avec un suffixe unique.")
    
    response = input("\nVoulez-vous procéder à la correction ? (oui/non): ").strip().lower()
    
    if response in ['oui', 'o', 'yes', 'y']:
        fix_duplicate_emails()
        print("\n✅ Correction terminée !")
        print("\n🚀 Vous pouvez maintenant relancer : python manage.py migrate")
    else:
        print("\n❌ Correction annulée.")

if __name__ == "__main__":
    main()
