from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from .utils import log_user_activity


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    log_user_activity(user, 'login', 'User logged in.')

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    log_user_activity(user, 'logout', 'User logged out.')