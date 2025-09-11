# hospitals/apps.py
from django.apps import AppConfig

class HospitalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hospitals'
    verbose_name = 'Gestion des Hôpitaux'