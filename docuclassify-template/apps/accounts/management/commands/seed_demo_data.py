from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Creates demo users for each RBAC role (admin, auditor, reviewer, viewer)."

    def handle(self, *args, **kwargs):
        demo_users = [
            ("demo_admin", "admin"),
            ("demo_auditor", "auditor"),
            ("demo_reviewer", "reviewer"),
            ("demo_viewer", "viewer"),
        ]
        for username, role in demo_users:
            user, created = User.objects.get_or_create(
                username=username, defaults={"role": role, "email": f"{username}@example.com"}
            )
            if created:
                user.set_password("demo1234")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created {username} ({role})"))
            else:
                self.stdout.write(f"{username} already exists")
