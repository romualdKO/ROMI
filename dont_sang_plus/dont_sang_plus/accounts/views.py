from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from .forms import DonorSignUpForm, HospitalSignUpForm
from django.contrib.auth.forms import AuthenticationForm

def donor_signup(request):
    if request.method == 'POST':
        form = DonorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = DonorSignUpForm()
    return render(request, 'signup.html', {
        'form': form,
        'user_type': 'donor',
        'title': 'Inscription Donneur'
    })

def hospital_signup(request):
    if request.method == 'POST':
        form = HospitalSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = HospitalSignUpForm()
    return render(request, 'signup.html', {
        'form': form,
        'user_type': 'hospital',
        'title': 'Inscription Hôpital'
    })

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})