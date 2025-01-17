# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegistrationForm
import os
from django.conf import settings
from django.contrib.auth import logout


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Du hast dich erfolgreich registriert!')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Ungültiger Benutzername oder Passwort')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def home(request):
    return render(request, 'accounts/home.html')


def user_logout(request):
    logout(request)
    return redirect('home') 