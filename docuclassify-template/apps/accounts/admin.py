from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("RBAC", {"fields": ("role", "organization")}),
    )
    list_display = ("username", "email", "role", "organization", "is_staff")
    list_filter = ("role", "organization")
