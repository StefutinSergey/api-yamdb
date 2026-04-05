"""Модели для приложения reviews."""

from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    ROLE_USER = 'user'
    ROLE_MODERATOR = 'moderator'
    ROLE_ADMIN = 'admin'
    ROLES = (
        (ROLE_USER, 'Пользователь'),
        (ROLE_MODERATOR, 'Модератор'),
        (ROLE_ADMIN, 'Администратор'),
    )
    role = models.CharField(
        max_length=max(len(choice[0]) for choice in ROLES),
        choices=ROLES,
        default=ROLE_USER,
        verbose_name='роль'
    )
    bio = models.TextField(blank=True, verbose_name='биография')
    confirmation_code = models.CharField(
        max_length=settings.CONFIRMATION_CODE_LENGTH,
        blank=True,
        null=True,
        verbose_name='код подтверждения'
    )
    email = models.EmailField(unique=True, verbose_name='email')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def is_moderator(self):
        return self.role == self.ROLE_MODERATOR

    def __str__(self):
        return self.username


class NameSlugModel(models.Model):
    """Абстрактная модель для объектов с полями name и slug."""

    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name="Имя",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Слаг",
    )

    class Meta:
        abstract = True
        ordering = ["name"]


class Category(NameSlugModel):
    """Модель для категорий произведений."""

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        # ordering = ["name"]

    def __str__(self):
        return self.name


class Genre(NameSlugModel):
    """Модель для жанров произведений."""

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        # ordering = ["name"]

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для произведений."""

    @staticmethod
    def current_year():
        return timezone.now().year

    name = models.CharField(max_length=256)
    year = models.IntegerField(
        validators=[
            MaxValueValidator(current_year),
        ]
    )
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="titles"
    )
    genre = models.ManyToManyField(Genre, related_name="titles")

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Призведения"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_review'
            )
        ]


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    pub_date = models.DateTimeField("Дата добавления", auto_now_add=True)
