from django.db import models

from django.contrib.auth.models import User

class ConfirmationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"ConfirmationCode(user={self.user}, code={self.code}, is_used={self.is_used})"
