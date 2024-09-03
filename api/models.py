from django.db import models
from django.utils.datetime_safe import datetime

from authorization.models import User


class ProjectSummary(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=80, verbose_name="Название таблицы", unique=True)

    class Meta:
        verbose_name = "Таблица"
        verbose_name_plural = "Таблицы"

    def __str__(self):
        return f"{self.name}"


class ProjectParameter(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=80, verbose_name="Название поля")
    project = models.ForeignKey(
        ProjectSummary,
        on_delete=models.CASCADE,
        related_name='parameters',
        related_query_name='parameters',
        verbose_name="Проект"
    )

    class Meta:
        verbose_name = "Поле"
        verbose_name_plural = "Поля"
        unique_together = ('project', 'name')

    def __str__(self):
        return f"{self.name} ({self.project.name})"


class TestResult(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    project_name = models.CharField(max_length=80, verbose_name="(!Устаревшее) Название проекта", null=True, blank=True)
    name = models.CharField(max_length=80, verbose_name="Имя указанное в игре", null=True, blank=True)
    ip = models.CharField(max_length=15, verbose_name="IP адрес")
    end_time = models.DateTimeField(default=datetime.utcnow, verbose_name="Дата отправки")
    duration = models.IntegerField(default=0, verbose_name="Времени заняло")

    project = models.ForeignKey(
        ProjectSummary,
        on_delete=models.CASCADE,
        related_name='results',
        related_query_name='results',
        verbose_name="Таблица",
        blank=True,
        null=True
    )

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name="Пользователь",
                             null=True, blank=True, related_name="test_results")

    def __str__(self):
        auth = False
        if self.user:
            auth = True
        return (f'{self.project.name if self.project else "???"}: {self.user.first_name if auth else self.name}'
                f' ({"Авторизован" if auth else "Неавторизован"})')

    class Meta:
        verbose_name = "Результат прохождения"
        verbose_name_plural = "Результаты прохождений"


class TestResultParameter(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    test_result = models.ForeignKey(TestResult,
                                    on_delete=models.CASCADE,
                                    related_name='parameters',
                                    blank=True,
                                    null=True
                                    )
    name = models.CharField(max_length=80, blank=True, null=True, verbose_name="(!Устаревшее) Название поля")
    value = models.CharField(max_length=500, verbose_name="Значение")

    project_parameter = models.ForeignKey(
        ProjectParameter,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.name or self.project_parameter.name} = {self.value}'

    class Meta:
        verbose_name = "Поле"
        verbose_name_plural = "Поля"
