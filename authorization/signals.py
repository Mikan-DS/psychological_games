import random
import string

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Settings

def generate_random_key(length=25):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@receiver(post_migrate)
def create_default_settings(sender, **kwargs):
    if not Settings.objects.exists():
        Settings.objects.create(vk_secret_key=generate_random_key())
