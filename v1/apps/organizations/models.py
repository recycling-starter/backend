from django.db import models


class Organization(models.Model):
    avatar = models.ImageField(
        upload_to='media/organizations'
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Название'
    )
    min_full_boxes = models.IntegerField(
        verbose_name='Количество полных коробок, необходимых для вывоза'
    )
    min_fullness_level_dropoff_call = models.IntegerField(
        verbose_name='Минимальный уровень заполненности контейнера для инициирования вывоза'
    )
    min_fullness_level_dropoff = models.IntegerField(
        verbose_name='Максимальный уровень заполненности контейнера для вывоза'
    )
    dropoff_email_to = models.CharField(
        verbose_name='E-mail для уведомлений',
        max_length=250
    )
    dropoff_email_from = models.CharField(
        verbose_name='E-mail для ответа',
        max_length=250
    )

    def __str__(self):
        return self.name


class Building(models.Model):
    address = models.CharField(
        max_length=250,
        verbose_name='Адрес'
    )
    organization = models.ForeignKey(
        Organization,
        verbose_name='Ответственная организация',
        null=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.address