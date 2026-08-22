from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for GlobeTrotter.
    Extends Django's AbstractUser so we keep username/password/auth
    machinery for free, and just bolt on the extra profile fields
    the app needs (per the User Profile / Settings screen).
    """
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_photo = models.ImageField(
        upload_to="profile_photos/", blank=True, null=True
    )
    language_preference = models.CharField(max_length=10, default="en")
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username
