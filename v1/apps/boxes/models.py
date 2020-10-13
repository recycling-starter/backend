from django.db import models

from v1.apps.organizations.models import Building
from v1.apps.users.models import User, User


class Box(models.Model):
    fullness = models.IntegerField(
        verbose_name='Заполненность',
        default=0
    )
    room = models.CharField(
        max_length=100,
        verbose_name='Расположение'
    )
    building = models.ForeignKey(
        Building,
        verbose_name='Здание привязки',
        on_delete=models.CASCADE
    )
    users = models.ManyToManyField(
        User,
        verbose_name='Ответственные пользователи'
    )
