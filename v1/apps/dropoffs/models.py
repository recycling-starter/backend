from django.db import models

from v1.apps.boxes.models import Box
from v1.apps.organizations.models import Organization, Building


class DropoffCall(models.Model):
    datetime_call = models.DateTimeField(
        verbose_name='Время вызова',
        auto_now_add=True
    )
    datetime_dropoff = models.DateTimeField(
        verbose_name='Время вывоза',
        null=True
    )
    building = models.ForeignKey(
        Building,
        verbose_name='Здание',
        on_delete=models.CASCADE
    )
    is_dropped = models.BooleanField(
        default=False
    )


class DropoffLog(models.Model):
    call = models.ForeignKey(
        DropoffCall,
        verbose_name='Вызов',
        on_delete=models.CASCADE
    )
    box = models.ForeignKey(
        Box,
        verbose_name='Коробка',
        on_delete=models.CASCADE
    )
    box_percent_dropped = models.IntegerField(
        verbose_name='Процент заполнения вывезен'
    )
