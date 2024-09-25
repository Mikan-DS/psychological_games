from datetime import timedelta

from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    phone = models.BigIntegerField(unique=True, null=True, blank=True, verbose_name='Номер телефона')

    objects = UserManager()

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class ConfirmationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"ConfirmationCode(user={self.user}, code={self.code}, is_used={self.is_used}, expires_at={self.expires_at})"

    @property
    def is_active(self):
        return not self.is_used and timezone.now() < self.expires_at

    class Meta:
        verbose_name = "Код подтверждения"
        verbose_name_plural = "Коды подтверждения"
        ordering = ['-expires_at']


class Settings(models.Model):
    confirmation_code_expiry = models.DurationField(
        default=timedelta(hours=1),
        verbose_name="Срок действия кода подтверждения")
    vk_token = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="VK токен")
    vk_confirmation_token = models.CharField(max_length=100,
                                             blank=True,
                                             null=True,
                                             verbose_name="VK токен подтверждения (Используется только при привязке)")
    vk_secret_key = models.CharField(max_length=100,
                                     blank=True,
                                     null=True,
                                     verbose_name="Секретный ключ для VK")
    vk_chat_url = models.CharField(
        max_length=255,
        default="https://vk.com/im?sel=-199827634",
        verbose_name="URL чата бота VK")

    host_url = models.URLField(
        max_length=255,
        default="http://localhost:8000/",
        verbose_name="Ссылка сайта"
    )
    pay_url = models.URLField(
        max_length=255,
        default="http://localhost:8000/",
        verbose_name="Ссылка сайта оплаты"
    )

    enot_code = models.CharField(max_length=10, verbose_name="Enot: Код", null=True, blank=True)

    yookassa_account_id = models.IntegerField(null=True, blank=True, verbose_name="Yookassa: Идентификатор магазина")
    yookassa_secret_key = models.CharField(
        max_length=70,
        null=True,
        blank=True,
        verbose_name="Yookassa: Секретный ключ")

    send_debug_messages = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Настройка"
        verbose_name_plural = "Настройки"

    def __str__(self):
        return "Настройка"

    def save(self, *args, **kwargs):
        if not self.pk and Settings.objects.exists():
            raise ValueError('Настройка уникальна, больше создавать нельзя!')

        return super(Settings, self).save(*args, **kwargs)


class Product(models.Model):
    article = models.CharField(max_length=255, verbose_name="Артикул", unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    verbose = models.CharField(max_length=255, verbose_name="Название")


class Purchase(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    ITEM_TYPES = [
        ('game', 'Игра'),
        ('game_consultation', 'Игра и консультация'),
    ]
    item_type = models.CharField(max_length=255, choices=ITEM_TYPES,
                                 verbose_name="Тип (устаревшее, необходимо использовать новый тип)",
                                 null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, verbose_name="Тип", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="purchases")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    paid = models.BooleanField(default=False, verbose_name="Оплачено")

    yookassa_order_id = models.CharField(max_length=255, verbose_name="ID платежа yookassa", null=True, blank=True)

    def __str__(self):
        return f"{self.get_item_type_display()} от {self.user} за {self.cost} - {'Оплачено' if self.paid else 'Не оплачено'}"

    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"


class ContactWay(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    method = models.CharField(max_length=255, verbose_name="Метод")
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Имя")

    def __str__(self):
        return self.name or self.method

    class Meta:
        verbose_name = "Способ контакта"
        verbose_name_plural = "Способы контакта"


class Age(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    value = models.CharField(max_length=255, verbose_name="Возраст")

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = "Возраст"
        verbose_name_plural = "Возрасты"


class ConsultationParameters(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    question = models.TextField(null=True, blank=True, verbose_name="Вопрос для консультации")
    age = models.ForeignKey(Age, on_delete=models.CASCADE, verbose_name="Возраст")
    GENDER_TYPES = [
        (True, 'М'),
        (False, 'Ж'),
    ]
    gender = models.BooleanField(default=True, choices=GENDER_TYPES, verbose_name="Пол")  # True = 'М', False = 'Ж'
    contact_way = models.ForeignKey(ContactWay, on_delete=models.CASCADE, verbose_name="Способ связи")
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE, verbose_name="Покупка")

    def __str__(self):
        return f"Консультация для {self.age}, {'М' if self.gender else 'Ж'}, через {self.contact_way}"

    class Meta:
        verbose_name = "Параметры консультации"
        verbose_name_plural = "Параметры консультаций"
