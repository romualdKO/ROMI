#!/usr/bin/env python
"""
Script de migration des données de SQLite vers PostgreSQL
pour l'application Don Sang Plus
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def setup_django():
    """Configuration de Django pour utiliser SQLite temporairement"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dont_sang_plus.settings')
    django.setup()

def export_data():
    """Exporter les données depuis SQLite"""
    print("🔄 Export des données depuis SQLite...")
    
    # Commande pour exporter les données
    execute_from_command_line(['manage.py', 'dumpdata', 
                              '--output=data_backup.json',
                              '--indent=2',
                              '--exclude=contenttypes',
                              '--exclude=auth.permission'])
    
    print("✅ Données exportées vers data_backup.json")

def import_data():
    """Importer les données vers PostgreSQL"""
    print("🔄 Import des données vers PostgreSQL...")
    
    # Commande pour importer les données
    execute_from_command_line(['manage.py', 'loaddata', 'data_backup.json'])
    
    print("✅ Données importées dans PostgreSQL")

def main():
    """Fonction principale"""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'export':
            setup_django()
            export_data()
        elif sys.argv[1] == 'import':
            setup_django()
            import_data()
        else:
            print("Usage: python migrate_data.py [export|import]")
    else:
        print("""
🔄 Script de migration Don Sang Plus

Usage:
  python migrate_data.py export   # Exporter depuis SQLite
  python migrate_data.py import   # Importer vers PostgreSQL

Instructions:
1. Avant de changer settings.py: python migrate_data.py export
2. Configurer PostgreSQL et modifier settings.py
3. Après migration Django: python migrate_data.py import
        """)

if __name__ == '__main__':
    main()