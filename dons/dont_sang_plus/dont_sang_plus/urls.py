from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('donations/', include('donations.urls')),
    
    # ✅ AJOUTE LES URLs DE RESET PASSWORD ICI (en dehors du if DEBUG)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html'
         ), name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ), name='password_reset_confirm'),
    
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), name='password_reset_complete'),
         
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ✅ GARDE SEULEMENT LES MEDIA FILES DANS LE if DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)