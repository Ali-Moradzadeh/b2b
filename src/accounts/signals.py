from .models import Profile, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=User)
def auto_create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    Profile.objects.get_or_create(user=instance)
    if instance.is_verified:
        Token.objects.get_or_create(user=instance)
