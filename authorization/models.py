from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class ConfirmationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField(default=timezone.now() + timedelta(days=1))

    def __str__(self):
        return f"ConfirmationCode(user={self.user}, code={self.code}, is_used={self.is_used}, expires_at={self.expires_at})"

    @property
    def is_active(self):
        return not self.is_used and timezone.now() < self.expires_at


class Settings(models.Model):
    confirmation_code_expiry = models.DurationField(default=timedelta(hours=1))
    vk_token = models.CharField(max_length=255, blank=True, null=True)
    vk_confirmation_token = models.CharField(max_length=100, blank=True, null=True)
    vk_secret_key = models.CharField(max_length=100, blank=True, null=True)
    vk_chat_url = models.CharField(max_length=255, default="https://vk.com/im?sel=-199827634")

    host_url = models.URLField(max_length=255, default="http://localhost:8000/")
    pay_url = models.URLField(max_length=255, default="http://localhost:8000/")

    send_debug_messages = models.BooleanField(default=True)

    def __str__(self):
        return (f"Settings(confirmation_code_expiry={self.confirmation_code_expiry}, "
                f"vk_token={self.vk_token}, vk_confirmation_token={self.vk_confirmation_token}, "
                f"vk_secret_key={self.vk_secret_key})")

    def save(self, *args, **kwargs):
        if not self.pk and Settings.objects.exists():
            raise ValueError('Настройка уникальна, больше создавать нельзя!')
        return super(Settings, self).save(*args, **kwargs)


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    item_type = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.item_type.isalnum() or ' ' in self.item_type or '.' in self.item_type:
            raise ValueError("Тип товара может содержать только латиницу без пробелов и точек: " + self.item_type)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    id = models.AutoField(primary_key=True)
    item_type = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.item_type} by {self.user} for {self.cost} - {'Paid' if self.paid else 'Not Paid'}"


class ContactWay(models.Model):
    id = models.AutoField(primary_key=True)
    method = models.CharField(max_length=255)

    def __str__(self):
        return self.method


class Age(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.value


class ConsultationParameters(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.TextField()
    age = models.ForeignKey(Age, on_delete=models.CASCADE)
    gender = models.BooleanField(default=True)  # True = 'М', False = 'Ж'
    contact_way = models.ForeignKey(ContactWay, on_delete=models.CASCADE)
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE)

    def __str__(self):
        return f"Consultation for {self.age}, {'М' if self.gender else 'Ж'}, via {self.contact_way}"
