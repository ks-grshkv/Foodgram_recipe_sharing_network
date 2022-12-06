from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models


class Roles(Enum):
    admin = 'admin'
    user = 'user'


class User(AbstractUser):
    CHOICES = (
        (Roles.admin.name, 'Администратор'),
        (Roles.user.name, 'Пользователь'),
    )
    first_name = models.CharField(
        max_length=150,
    )
    last_name = models.CharField(
        max_length=150,
    )
    email = models.EmailField(
        max_length=254,
    )
    username = models.CharField(
        max_length=150,
        unique=True
    )
    password = models.CharField(
        max_length=150
    )
    role = models.CharField(
        verbose_name='Пользовательская роль',
        max_length=10,
        choices=CHOICES,
        default=Roles.user.name,
    )
    following = models.ManyToManyField(
        "self",
        through='Subscription',
        related_name="followers",
        verbose_name="following",
        symmetrical=False)

    @property
    def is_admin(self):
        return self.role == Roles.admin.name

    @property
    def is_user(self):
        return self.role == Roles.user.name

    class Meta:
        ordering = ('-username',)
        verbose_name = 'Пользователи'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_to',
        blank=True,
        null=True,
        verbose_name='Автор'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        blank=True,
        null=True,
        verbose_name='Пользователь'
    )

    class Meta:
        ordering = ('-user',)
        verbose_name = 'Подписки'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user} follows {self.author}'
