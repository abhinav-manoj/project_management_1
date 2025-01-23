from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import File

@receiver(pre_save, sender=File)
def set_created_user(sender, instance, **kwargs):
    # Only set the created_user if it's not already set and a user is available in the request
    if not instance.pk and hasattr(instance, '_request') and instance._request.user.is_authenticated:
        instance.created_user = instance._request.user
