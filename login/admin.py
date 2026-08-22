from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("username", "email", "first_name",
                    "last_name", "is_staff", "created_at")
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("phone_number",
         "profile_photo", "language_preference")}),
    )


admin.site.register(User, CustomUserAdmin)
