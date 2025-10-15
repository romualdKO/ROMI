from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    # Dashboards principaux
    path('', views.dashboard, name='dashboard'),
    path('donor-dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('hospital-dashboard/', views.hospital_dashboard, name='hospital_dashboard'),
    
    # ✅ CORRIGE LES URLs DES DEMANDES DE SANG
    path('create-blood-request/', views.create_blood_request, name='create_blood_request'),
    path('create-request/', views.create_blood_request, name='create_request'),  # URL alternative
    path('blood-request/<int:request_id>/edit/', views.edit_blood_request, name='edit_blood_request'),
    path('edit-request/<int:request_id>/', views.edit_blood_request, name='edit_request'),  # URL alternative
    path('request/<int:request_id>/edit/', views.edit_blood_request, name='edit_blood_request_short'),  # URL courte
    
    # Gestion des réponses
    path('responses/<int:request_id>/', views.view_responses, name='view_responses'),
    path('respond/<int:request_id>/', views.respond_to_request, name='respond_to_request'),
    path('response/<int:response_id>/update/<str:status>/', views.update_response_status, name='update_response_status'),
    path('my-responses/', views.my_responses, name='my_responses'),
    path('response/<int:response_id>/', views.response_detail, name='response_detail'),
    path('request/<int:request_id>/', views.request_detail, name='request_detail'),
    path('update-status/<int:response_id>/<str:status>/', views.update_response_status, name='update_response_status'),
    path('api/message-counts/', views.api_message_counts, name='api_message_counts'),
    
    # Gestion des statuts de demandes (pour hôpitaux)
    path('request/<int:request_id>/status/<str:new_status>/', views.update_request_status, name='update_request_status'),
    
    # ... autres URLs ...
    # Chat et communication
    path('chat/<int:response_id>/', views.chat_with_donor, name='chat_with_donor'),
    
    # Disponibilité des donneurs
    path('update-availability/', views.update_availability, name='update_availability'),
    path('availability-updated/', views.update_availability, name='update_availability_page'),
    
    # Profil utilisateur
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    
    # Messages et Historique
    path('donor-messages/', views.donor_messages, name='donor_messages'),
    path('hospital-messages/', views.hospital_messages, name='hospital_messages'),
    path('donor-history/', views.donor_history, name='donor_history'),
    path('hospital-history/', views.hospital_history, name='hospital_history'),
    
    # Attestation
    path('attestation/<int:response_id>/', views.donation_attestation, name='donation_attestation'),
    
    # Don rapide
    path('quick-donate/<int:request_id>/', views.quick_donate, name='quick_donate'),
]