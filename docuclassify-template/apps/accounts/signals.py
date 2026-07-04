from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    # Hook point: send welcome email, provision default permissions,
    # create tenant-scoped resources, etc.
    if created:
        pass
