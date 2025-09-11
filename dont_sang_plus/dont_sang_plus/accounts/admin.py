# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'hospital_name_or_username', 'email', 'user_type', 'verification_status_badge', 
        'date_joined', 'quick_actions'
    ]
    list_filter = ['user_type', 'verification_status', 'is_verified', 'hospital_type', 'date_joined']
    search_fields = ['username', 'email', 'hospital_name', 'first_name', 'last_name']
    
    # ✅ Filtre pour voir seulement les hôpitaux en attente
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.GET.get('pending_hospitals'):
            return qs.filter(user_type='hospital', verification_status='pending')
        return qs
    
    def hospital_name_or_username(self, obj):
        if obj.user_type == 'hospital':
            return format_html('<strong>{}</strong>', obj.hospital_name or obj.username)
        return f"{obj.get_full_name()} ({obj.username})"
    hospital_name_or_username.short_description = 'Nom/Établissement'
    
    def verification_status_badge(self, obj):
        if obj.user_type == 'hospital':
            if obj.verification_status == 'pending':
                return format_html(
                    '<span class="badge" style="background-color: orange; color: white; padding: 5px;">⏳ EN ATTENTE</span>'
                )
            elif obj.verification_status == 'approved':
                return format_html(
                    '<span class="badge" style="background-color: green; color: white; padding: 5px;">✅ APPROUVÉ</span>'
                )
            elif obj.verification_status == 'rejected':
                return format_html(
                    '<span class="badge" style="background-color: red; color: white; padding: 5px;">❌ REJETÉ</span>'
                )
        return '-'
    verification_status_badge.short_description = 'Statut'
    
    def quick_actions(self, obj):
        if obj.user_type == 'hospital' and obj.verification_status == 'pending':
            return format_html(
                '<a class="button" href="/admin/accounts/customuser/{}/change/" style="background: green; color: white; padding: 5px; margin: 2px;">✅ Valider</a>'
                '<a class="button" href="/admin/accounts/customuser/{}/change/" style="background: red; color: white; padding: 5px; margin: 2px;">❌ Rejeter</a>',
                obj.id, obj.id
            )
        return '-'
    quick_actions.short_description = 'Actions rapides'
    
    # ✅ Actions en lot pour valider/rejeter plusieurs hôpitaux
    actions = ['approve_hospitals', 'reject_hospitals']
    
    def approve_hospitals(self, request, queryset):
        approved_count = 0
        for user in queryset.filter(user_type='hospital', verification_status='pending'):
            user.verification_status = 'approved'
            user.is_verified = True
            user.verified_at = timezone.now()
            user.verified_by = request.user
            user.save()
            
            # Email automatique
            try:
                send_mail(
                    subject='🎉 Compte validé - Don Sang Plus',
                    message=f'Félicitations {user.get_full_name()} !\n\n'
                           f'Votre compte pour {user.hospital_name} a été validé.\n'
                           f'Vous pouvez maintenant vous connecter et utiliser la plateforme.\n\n'
                           f'Connexion : {request.build_absolute_uri("/accounts/login/")}\n\n'
                           f'Équipe Don Sang Plus',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except:
                pass
            
            approved_count += 1
        
        self.message_user(request, f'✅ {approved_count} hôpital(s) approuvé(s) et notifié(s).')
    
    approve_hospitals.short_description = "✅ Approuver les hôpitaux sélectionnés"
    
    def reject_hospitals(self, request, queryset):
        rejected_count = 0
        for user in queryset.filter(user_type='hospital'):
            user.verification_status = 'rejected'
            user.is_verified = False
            user.save()
            rejected_count += 1
        
        self.message_user(request, f'❌ {rejected_count} hôpital(s) rejeté(s).')
    
    reject_hospitals.short_description = "❌ Rejeter les hôpitaux sélectionnés"