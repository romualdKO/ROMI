from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentification
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Inscription
    path('signup/donor/', views.donor_signup, name='donor_signup'),
    path('signup/hospital/', views.hospital_signup, name='hospital_signup'),
    
    # Dashboard général
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # ✅ RÉINITIALISATION MOT DE PASSE
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html',
             email_template_name='registration/password_reset_email.html',
             success_url='/accounts/password-reset/done/'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/accounts/reset/done/'
         ), 
         name='password_reset_confirm'),
    
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # Validation rapide hôpital (admin)
    path('quick-validate/<int:user_id>/', views.quick_validate_hospital, name='quick_validate_hospital'),
    
    # Autres vues de déconnexion (compatibilité)
    path('logout-view/', views.LogoutView, name='logout_view'),
    path('logout-default/', views.logout_default_user, name='logout_default'),
]