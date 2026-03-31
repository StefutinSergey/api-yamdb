from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator


User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='titles', blank=True, null=True
    )

    year = models.IntegerField(
        validators=[
            MinValueValidator(0000),
            MaxValueValidator(2100)
        ],
    )

    def __str__(self):
        return self.name
    

class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='reviews'
    )
    title_id = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10)
        ],
    )


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='comments'
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True
    )
