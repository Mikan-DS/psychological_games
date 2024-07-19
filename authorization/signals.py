import string

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Settings, Age, ContactWay, OrderItem
from .utils import generate_random_code


@receiver(post_migrate)
def create_default_settings(sender, **kwargs):
    if not Settings.objects.exists():
        Settings.objects.create(vk_secret_key=generate_random_code(25, chars=string.ascii_letters+string.digits))

    if not Age.objects.exists():
        default_ages = ["10-12 ЛЕТ", "12-14 ЛЕТ", "14-16 ЛЕТ", "16-18 ЛЕТ", "КОНСУЛЬТАЦИЯ ДЛЯ РОДИТЕЛЯ"]
        for age in default_ages:
            Age.objects.create(value=age)

    if not ContactWay.objects.exists():
        default_contact_ways = ["phone", "telegram", "whatsapp", "viber"]
        for method in default_contact_ways:
            ContactWay.objects.create(method=method)

    if not OrderItem.objects.exists():
        default_order_items = ["game", "game_consultation"]
        for item_type in default_order_items:
            OrderItem.objects.create(name=item_type, item_type=item_type)
