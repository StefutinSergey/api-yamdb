"""Модели для приложения reviews."""

from datetime import datetime

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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

    pass


class Genre(NameSlugModel):
    """Модель для жанров произведений."""

    pass


class Title(RepresentModel):
    """Модель для произведений."""

    name = models.CharField(max_length=256)
    year = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(datetime.now().year),
        ]
    )
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(Genre, related_name="titles")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="titles"
    )
