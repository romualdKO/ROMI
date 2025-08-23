# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('signup/donor/', views.donor_signup, name='donor_signup'),
    path('signup/hospital/', views.hospital_signup, name='hospital_signup'),
    path('login/', views.custom_login, name='login'),
]