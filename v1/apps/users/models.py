import six
from django.contrib.auth.models import User, AbstractUser, UserManager
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import models

from v1.apps.organizations.models import Organization, Building


# from django.utils import six

class CustomUserManager(UserManager):
    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user



class User(AbstractUser):
    phone = models.BigIntegerField(
        verbose_name='Номер телефона',
        null=True
    )
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    room = models.CharField(
        max_length=100,
        verbose_name='Расположение',
        null=True
    )
    building = models.ForeignKey(
        Building,
        verbose_name='Здание',
        on_delete=models.CASCADE,
        null=True
    )
    email = models.EmailField(
        verbose_name='email address',
        blank=True,
        unique=True
    )
    username = models.CharField(
        null=True,
        max_length=150,
        blank=True
    )
    first_name = models.CharField(max_length=150)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                six.text_type(user.pk) + six.text_type(timestamp) +
                six.text_type(user.is_active)
        )


account_activation_token = TokenGenerator()
