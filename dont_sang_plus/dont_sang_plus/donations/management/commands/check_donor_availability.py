"""
Commande Django pour vérifier la disponibilité des donneurs
Usage: python manage.py check_donor_availability
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from donations.models import DonorAvailability, DonationResponse
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Affiche la disponibilité de tous les donneurs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Vérifier un donneur spécifique par username',
        )
        parser.add_argument(
            '--available',
            action='store_true',
            help='Afficher uniquement les donneurs disponibles',
        )
        parser.add_argument(
            '--locked',
            action='store_true',
            help='Afficher uniquement les donneurs verrouillés',
        )

    def handle(self, *args, **options):
        self.stdout.write('=' * 100)
        self.stdout.write(self.style.SUCCESS('🩸 DISPONIBILITÉ DES DONNEURS'))
        self.stdout.write('=' * 100)
        self.stdout.write('')

        # Filtrer les donneurs
        if options['username']:
            donors = User.objects.filter(user_type='donor', username=options['username'])
            if not donors.exists():
                self.stdout.write(self.style.ERROR(f'❌ Aucun donneur trouvé avec le username: {options["username"]}'))
                return
        else:
            donors = User.objects.filter(user_type='donor')

        if not donors.exists():
            self.stdout.write(self.style.WARNING('⚠️  Aucun donneur dans la base de données'))
            return

        today = timezone.now().date()
        available_count = 0
        locked_count = 0

        for donor in donors:
            availability, created = DonorAvailability.objects.get_or_create(donor=donor)
            
            # Auto-déblocage
            availability.auto_unlock()
            availability.refresh_from_db()
            
            is_available = availability.is_currently_available()
            
            # Filtrer selon les options
            if options['available'] and not is_available:
                continue
            if options['locked'] and is_available:
                continue
            
            # Compter
            if is_available:
                available_count += 1
            else:
                locked_count += 1
            
            # Affichage
            self.stdout.write('')
            self.stdout.write(f'👤 {self.style.HTTP_INFO(donor.username)} - {donor.get_full_name()}')
            self.stdout.write(f'   Email: {donor.email}')
            self.stdout.write(f'   Groupe sanguin: {self.style.WARNING(donor.blood_type or "Non renseigné")}')
            
            # Statut de disponibilité
            if is_available:
                self.stdout.write(f'   Statut: {self.style.SUCCESS("✅ DISPONIBLE")}')
            else:
                self.stdout.write(f'   Statut: {self.style.ERROR("❌ INDISPONIBLE")}')
                lock_reason = availability.get_lock_reason()
                if lock_reason:
                    self.stdout.write(f'   Raison: {lock_reason}')
            
            # Détails de disponibilité
            self.stdout.write(f'   is_available (DB): {availability.is_available}')
            self.stdout.write(f'   next_available_date: {availability.next_available_date or "Aucune"}')
            
            # Historique des dons
            completed_responses = DonationResponse.objects.filter(donor=donor, status='completed')
            accepted_responses = DonationResponse.objects.filter(donor=donor, status='accepted')
            pending_responses = DonationResponse.objects.filter(donor=donor, status='pending')
            
            self.stdout.write(f'   Réponses aux demandes:')
            self.stdout.write(f'      - Complétées: {self.style.SUCCESS(completed_responses.count())}')
            self.stdout.write(f'      - Acceptées: {self.style.WARNING(accepted_responses.count())}')
            self.stdout.write(f'      - En attente: {pending_responses.count()}')
            
            # Dernier don complété
            if completed_responses.exists():
                last_completed = completed_responses.order_by('-response_date').first()
                expected_lock_until = last_completed.response_date.date() + timedelta(days=90)
                days_since = (today - last_completed.response_date.date()).days
                
                self.stdout.write(f'   Dernier don complété: {last_completed.response_date.date()} (il y a {days_since} jours)')
                self.stdout.write(f'   Verrouillage attendu jusqu\'au: {expected_lock_until}')
                
                # Vérifier la cohérence
                if expected_lock_until > today:
                    if is_available:
                        self.stdout.write(self.style.ERROR('      ⚠️  INCOHÉRENCE: Le donneur devrait être verrouillé!'))
                else:
                    if not is_available:
                        self.stdout.write(self.style.WARNING('      ⚠️  Le verrouillage devrait être expiré'))
            
            self.stdout.write('-' * 100)

        # Résumé
        self.stdout.write('')
        self.stdout.write('=' * 100)
        self.stdout.write(self.style.SUCCESS('📊 RÉSUMÉ'))
        self.stdout.write('=' * 100)
        self.stdout.write(f'Total de donneurs: {donors.count()}')
        self.stdout.write(f'{self.style.SUCCESS("Disponibles")}: {available_count}')
        self.stdout.write(f'{self.style.ERROR("Verrouillés")}: {locked_count}')
        
        if available_count > 0:
            percentage = (available_count / donors.count()) * 100
            self.stdout.write(f'Taux de disponibilité: {percentage:.1f}%')
        
        self.stdout.write('')
