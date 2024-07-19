import os
import shutil
import zipfile

from django.core.files import File
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete


class Game(models.Model):
    title = models.CharField(max_length=200, unique=True)
    archive = models.FileField(upload_to='games/')
    url = models.SlugField(max_length=200)
    # index = models.FileField(upload_to='games/misc/', null=True, blank=True)

    def __str__(self):
        return self.title

class GameFile(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    file = models.FileField(upload_to='games/', null=True, blank=True)
    is_index = models.BooleanField(default=False)


@receiver(post_save, sender=Game)
def unpack_archive(sender, instance: Game, **kwargs):
    if instance.archive:
        archive_path = instance.archive.path
        extract_path = os.path.join(os.path.dirname(archive_path), "unpacking", instance.title)

        # Удалить папку, если она уже существует
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        if os.path.exists(os.path.join(os.path.dirname(archive_path), instance.title)):
            shutil.rmtree(os.path.join(os.path.dirname(archive_path), instance.title))

        # Создать папку и распаковать архив
        os.makedirs(extract_path)
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)


        if not GameFile.objects.filter(game=instance).exists():
            # Проверка наличия index.html
            index_html_path = None

            for root, dirs, files in os.walk(extract_path):
                if index_html_path:
                    pass
                elif 'index.html' in files:
                    index_html_path = os.path.join(root, 'index.html')

                elif len(dirs) == 1 and 'index.html' in os.listdir(os.path.join(root, dirs[0])):
                    index_html_path = os.path.join(root, dirs[0], 'index.html')
                for file in files:
                    file_html_path = os.path.join(root, file)
                    gamefile = GameFile(game=instance, is_index=file_html_path==index_html_path)
                    with open(file_html_path, 'rb') as file_html:
                        gamefile.file.save(

                            os.path.join(
                                root.replace(os.path.join(os.path.dirname(archive_path), "unpacking"), ""),
                                file),
                            File(
                                file_html,
                                file
                            ))
            shutil.rmtree(extract_path)

            # # Обновить поле index если index.html найден
            # if index_html_path:
            #     instance.index.save(os.path.join(instance.title, os.path.basename(index_html_path)), File(open(index_html_path, 'rb')), save=False)
            #     instance.save(update_fields=['index'])




@receiver(pre_save, sender=Game)
def delete_old_archive(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Game.objects.get(pk=instance.pk)
            archive_path = old_instance.archive.path
            extract_path = os.path.join(os.path.dirname(archive_path), old_instance.title)
            new_extract_path = os.path.join(os.path.dirname(archive_path), instance.title)
            if extract_path != new_extract_path:
                if os.path.exists(new_extract_path):
                    shutil.rmtree(new_extract_path)
                GameFile.objects.filter(game=instance).delete()
                shutil.move(extract_path, os.path.join(os.path.dirname(archive_path), "unpacking", instance.title))

            if archive_path != instance.archive.path:
                old_instance.archive.delete(save=False)


        except Game.DoesNotExist:
            pass

@receiver(post_delete, sender=Game)
def delete_archive_on_delete(sender, instance, **kwargs):

    # Удалить распакованную папку
    extract_path = os.path.join(os.path.dirname(instance.archive.path), instance.title)
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)

    if instance.archive:
        instance.archive.delete(save=False)
