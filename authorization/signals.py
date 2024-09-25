import string

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Settings, Age, ContactWay, Product, Purchase
from .utils import generate_random_code


@receiver(post_migrate)
def create_default_settings(sender, **kwargs):
    if not Settings.objects.exists():
        Settings.objects.create(vk_secret_key=generate_random_code(25, chars=string.ascii_letters + string.digits))

    if not Age.objects.exists():
        default_ages = ["10-12 ЛЕТ", "12-14 ЛЕТ", "14-16 ЛЕТ", "16-18 ЛЕТ", "КОНСУЛЬТАЦИЯ ДЛЯ РОДИТЕЛЯ"]
        for age in default_ages:
            Age.objects.create(value=age)

    if not ContactWay.objects.exists():
        default_contact_ways = [
            ("phone", "По телефону"),
            ("telegram", "Телеграм"),
            ("whatsapp", "Whatsapp"),
            ("viber", "Viber")]
        for method, name in default_contact_ways:
            ContactWay.objects.create(method=method, name=name)

    if not Product.objects.exists():
        default_product = [
            ("game", "Игра", 500),
            ("game_consultation", "Игра и консультация", 3500)
        ]
        for article, verbose, price in default_product:
            Product.objects.create(
                article=article,
                price=price,
                verbose=verbose
            )

    if Product.objects.exists():

        for purchase in Purchase.objects.all():
            try:
                if not purchase.product:
                    product = Product.objects.get(article=purchase.item_type)
                    purchase.product = product
                    purchase.item_type = None
                    purchase.save()
            except Exception as e:
                print("Purchase cannot be added: ", purchase.item_type, repr(e))
