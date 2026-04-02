"""Сериалидзаторы для моделей приложения reviews."""

from rest_framework import serializers

from reviews.models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ("name", "slug")
        read_only_fields = ("id",)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ("name", "slug")


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, queryset=Genre.objects.all(), slug_field="slug"
    )

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="slug"
    )

    class Meta:
        model = Title
        fields = ("name", "year", "description", "genre", "category")

    def create(self, validated_data):
        genres = validated_data.pop("genre")
        category = validated_data.pop("category")

        title = Title.objects.create(**validated_data, category=category)
        title.genre.set(genres)
        title.save()

        return title


"""
Каждый ресурс описан в документации: 
указаны эндпоинты (адреса, по которым можно сделать запрос), 
разрешённые типы запросов, 
права доступа и дополнительные параметры, когда это необходимо.
"""
