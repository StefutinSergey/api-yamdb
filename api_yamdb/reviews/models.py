from django.db import models
from django.core.exceptions import ValidationError


class RepresentModel(models.Model):
    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class SlugCheckModel(RepresentModel):
    # Список моделей для проверки кросс-уникальности slug,
    # исключая модель-наследника
    slug_models = []

    def clean(self):
        """
        Кросс-модельная проверка уникальности поля slug.

        Сохранение встроенных проверок Django перед дополнительной валидацией.
        Циклическая проверка уникальности slug по моделям, использующим поле
        slug.
        """
        super().clean()
        for model_name in self.slug_models:
            model_class = models.apps.get_model(
                app_label="reviews", model_name=model_name
            )
            if model_class.objects.filter(slug=model_class.slug).exists():
                raise ValidationError(
                    f"Slug уже используется в {model_class.__name__}",
                )

        class Meta:
            abstract = True


class NameSlugModel(SlugCheckModel):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        abstract = True


class Category(NameSlugModel):
    slug_models = ["Genre"]


class Genre(NameSlugModel):
    slug_models = ["Category"]


class Title(RepresentModel):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="titles"
    )
    genre = models.ManyToManyField(Genre, related_name="titles")
