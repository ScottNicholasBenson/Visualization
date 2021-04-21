from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User, Group
from .models import Profile
from django_otp.plugins.otp_totp.models import TOTPDevice


@receiver(post_save, sender=User)
def init_new_user(instance, created, raw, **kwargs):
    if created:
        # Profile.objects.create(
        #     user_id=instance)
        user_id = Profile.objects.values('user_id').filter(user=instance)
