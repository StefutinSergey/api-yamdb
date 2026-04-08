from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.conf import settings

from .constants import (
    CONFIRMATION_CODE_LENGTH,
    MAX_USERNAME_LENGTH,
    MAX_EMAIL_LENGTH,
    REVIEW_SCORE_MIN,
    REVIEW_SCORE_MAX,
)


def current_year():
    return timezone.now().year


class User(AbstractUser):
    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=settings.USERNAME_REGEX,
                message="Имя пользователя может содержать только латинские "
                        "буквы, цифры и символы",
            ),
        ],
        verbose_name="имя пользователя",
    )
    ROLE_USER = "user"
    ROLE_MODERATOR = "moderator"
    ROLE_ADMIN = "admin"
    ROLES = (
        (ROLE_USER, "Пользователь"),
        (ROLE_MODERATOR, "Модератор"),
        (ROLE_ADMIN, "Администратор"),
    )
    role = models.CharField(
        max_length=max(len(choice[0]) for choice in ROLES),
        choices=ROLES,
        default=ROLE_USER,
        verbose_name="роль",
    )
    bio = models.TextField(blank=True, verbose_name="описание")
    confirmation_code = models.CharField(
        max_length=CONFIRMATION_CODE_LENGTH,
        blank=True,
        null=True,
        verbose_name="код подтверждения",
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        verbose_name="электронная почта"
    )

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = ('username',)

    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_staff

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
        verbose_name="Идентификатор",
    )

    class Meta:
        abstract = True
        ordering = ("name",)

    def __str__(self):
        return self.name


class Category(NameSlugModel):
    """Модель для категорий произведений."""

    class Meta(NameSlugModel.Meta):
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Genre(NameSlugModel):
    """Модель для жанров произведений."""

    class Meta(NameSlugModel.Meta):
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Title(models.Model):
    """Модель для произведений."""

    name = models.CharField(max_length=256)
    year = models.IntegerField(
        validators=[
            MaxValueValidator(current_year),
        ]
    )
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
    )
    genre = models.ManyToManyField(Genre)

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Призведения"
        ordering = ("name",)
        default_related_name = "titles"  # автоматически для всех связей

    def __str__(self):
        return self.name


class BaseAuthorTextPubDateModel(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="автор")
    text = models.TextField(verbose_name="текст")
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="дата публикации")

    class Meta:
        abstract = True
        ordering = ("-pub_date",)
        default_related_name = "%(class)ss"


class Review(BaseAuthorTextPubDateModel):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='произведение'
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(REVIEW_SCORE_MIN),
            MaxValueValidator(REVIEW_SCORE_MAX),
        ],
        verbose_name="оценка",
    )

    class Meta(BaseAuthorTextPubDateModel.Meta):
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ("pub_date",)
        constraints = [
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_review")
        ]


class Comment(BaseAuthorTextPubDateModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='отзыв'
    )

    class Meta(BaseAuthorTextPubDateModel.Meta):
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
