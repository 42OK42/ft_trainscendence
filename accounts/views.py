import os
import json
import requests
from dotenv import load_dotenv

from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login as auth_login

from .forms import CustomUserCreationForm
from .models import CustomUser

# Load environment variables from secrets.env
load_dotenv(os.path.join(settings.BASE_DIR, 'secrets.env'))

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8000/accounts/callback/'

def login(request):
    url = f"https://api.intra.42.fr/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
    return redirect(url)

def callback(request):
    code = request.GET.get('code')
    token_response = requests.post('https://api.intra.42.fr/oauth/token', data={
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }).json()

    access_token = token_response.get('access_token')
    user_response = requests.get('https://api.intra.42.fr/v2/me', headers={
        'Authorization': f'Bearer {access_token}',
    }).json()

    # Extract user details from the API response
    username = user_response.get('login')
    first_name = user_response.get('first_name')
    last_name = user_response.get('last_name')
    picture = user_response['image']['versions']['small']

    # Format the API response with each comma starting on a new line
    formatted_api_response = json.dumps(user_response, indent=2).replace(',', ',\n')

    # Save or update the user in the database
    user, created = CustomUser.objects.get_or_create(username=username, defaults={
        'first_name': first_name,
        'last_name': last_name,
        'picture': picture,
        'api_response': formatted_api_response,
    })
    if not created:
        # Update the user's details if they already exist
        user.first_name = first_name
        user.last_name = last_name
        user.picture = picture
        user.api_response = formatted_api_response
        user.save()

    # Store the API response in the session
    request.session['api_response'] = formatted_api_response

    auth_login(request, user)
    return redirect('home')

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
