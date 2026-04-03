from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='user')
    bio = models.TextField(blank=True, verbose_name='Биография')
    confirmation_code = models.CharField(max_length=6, blank=True, null=True)
    email = models.EmailField(unique=True)

    def is_admin(self):
        """Возвращает True, если пользователь администратор."""
        return self.role == 'admin' or self.is_superuser or self.is_staff

    def is_moderator(self):
        """Возвращает True, если пользователь модератор."""
        return self.role == 'moderator'

    def __str__(self):
        return self.username
