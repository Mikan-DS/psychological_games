from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class ConfirmationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField(default=datetime.now() + timedelta(days=1))

    def __str__(self):
        return f"ConfirmationCode(user={self.user}, code={self.code}, is_used={self.is_used}, expires_at={self.expires_at})"

    @property
    def is_active(self):
        return not self.is_used and datetime.now() < self.expires_at


class Settings(models.Model):
    confirmation_code_expiry = models.DurationField(default=timedelta(hours=1))

    def save(self, *args, **kwargs):
        if not self.pk and Settings.objects.exists():
            raise ValueError('Настройка уникальна, больше создавать нельзя!')
        return super(Settings, self).save(*args, **kwargs)
