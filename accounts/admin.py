from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('picture', 'wins', 'draws', 'losses', 'display_name', 'api_response')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('picture', 'wins', 'draws', 'losses', 'display_name', 'api_response')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'wins', 'draws', 'losses', 'display_name', 'picture', 'api_response')

admin.site.register(CustomUser, CustomUserAdmin)