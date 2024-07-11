import random
import string

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Settings
from .utils import generate_random_code

@receiver(post_migrate)
def create_default_settings(sender, **kwargs):
    if not Settings.objects.exists():
        Settings.objects.create(vk_secret_key=generate_random_code(25, chars=string.ascii_letters+string.digits))
