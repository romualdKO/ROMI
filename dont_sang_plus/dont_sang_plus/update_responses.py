"""
Script pour mettre à jour les réponses en attente vers acceptées
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from donations.models import DonationResponse

# Mettre à jour toutes les réponses "pending" vers "accepted"
updated_count = DonationResponse.objects.filter(status='pending').update(status='accepted')

print(f"✅ {updated_count} réponse(s) mise(s) à jour de 'pending' → 'accepted'")

# Afficher le résumé
total = DonationResponse.objects.count()
accepted = DonationResponse.objects.filter(status='accepted').count()
completed = DonationResponse.objects.filter(status='completed').count()
rejected = DonationResponse.objects.filter(status='rejected').count()

print(f"\n📊 Résumé des statuts:")
print(f"   Total: {total}")
print(f"   ✅ Acceptées: {accepted}")
print(f"   ✔️ Complétées: {completed}")
print(f"   ❌ Refusées: {rejected}")
