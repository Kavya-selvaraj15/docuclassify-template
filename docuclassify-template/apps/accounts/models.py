from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    """
    RBAC roles. Extend this list per tenant/org as needed.
    Kept as TextChoices (not a separate table) for simplicity in this
    template — swap for a full Role model if you need per-tenant
    custom roles or dynamic permission sets.
    """
    ADMIN = "admin", "Admin"
    AUDITOR = "auditor", "Auditor"
    REVIEWER = "reviewer", "Reviewer"
    VIEWER = "viewer", "Viewer"


class User(AbstractUser):
    """
    Custom user model so RBAC role lives on the user from day one.
    Swapping AUTH_USER_MODEL later is painful — this template starts
    correctly.
    """
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    organization = models.CharField(max_length=150, blank=True, help_text="Tenant / org name for multi-tenant setups")

    def has_role(self, *roles):
        return self.role in roles

    def __str__(self):
        return f"{self.username} ({self.role})"
