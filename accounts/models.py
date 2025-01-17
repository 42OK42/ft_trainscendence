from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    picture = models.URLField(null=True, blank=True)
    wins = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    api_response = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username