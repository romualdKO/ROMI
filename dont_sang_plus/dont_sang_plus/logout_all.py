#!/usr/bin/env python
"""
Script pour déconnecter tous les utilisateurs
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
django.setup()

from django.contrib.sessions.models import Session

# Supprimer toutes les sessions actives
Session.objects.all().delete()
print("✅ Toutes les sessions ont été supprimées.")
print("🔓 Aucun utilisateur n'est connecté maintenant.")
