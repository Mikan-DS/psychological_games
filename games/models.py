import os
import shutil
import zipfile

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete


# class Game(models.Model):
#     title = models.CharField(max_length=200, unique=True, verbose_name="Название")
#     archive = models.FileField(upload_to='games/', verbose_name="Архив", null=True, blank=True)
#     reload = models.BooleanField(default=False, verbose_name="Перезагрузить с диска сервера (unpacking/Название игры)")
#     url = models.SlugField(max_length=200, verbose_name="URL")
class Game(models.Model):

    ACCESS_CHOICES = [
        (1, 'Персонал'),
        (2, 'Купившие игру (пока == авторизован)'),
        (3, 'Авторизован'),
        (4, 'Все'),
    ]

    id = models.AutoField(primary_key=True, verbose_name="ID")
    title = models.CharField(max_length=200, verbose_name="Название")
    url = models.SlugField(max_length=200, verbose_name="URL", unique=True)
    folder = models.CharField(max_length=200, verbose_name="Папка на сервере", unique=True)
    access = models.IntegerField(choices=ACCESS_CHOICES, verbose_name="Доступ", default=1)



    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Игра"
        verbose_name_plural = "Игры"
        ordering = ['title']

    def has_access(self, user: User) -> bool:
        if self.access == 1:
            return user.is_staff
        elif self.access in (2, 3):
            return user.is_authenticated
        else:
            return True


@receiver(post_delete, sender=Game)
def delete_archive_on_delete(sender, instance: Game, **kwargs):
    # Удалить распакованную папку
    extract_path = os.path.join(settings.MEDIA_ROOT, 'games', instance.folder)
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)

