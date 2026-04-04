"""Модели для приложения reviews."""

from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator


User = get_user_model()


class RepresentModel(models.Model):
    """Абстрактная модель для представления объектов с полем name."""

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class NameSlugModel(RepresentModel):
    """Абстрактная модель для объектов с полями name и slug."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        abstract = True


class Category(NameSlugModel):
    """Модель для категорий произведений."""

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]


class Genre(NameSlugModel):
    """Модель для жанров произведений."""

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ["name"]


class Title(RepresentModel):
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


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    title_id = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name="reviews"
    )
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    pub_date = models.DateTimeField("Дата добавления", auto_now_add=True)
