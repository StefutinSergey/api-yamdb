from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import RegexValidator

from reviews.models import Comment, Review, Category, Title, Genre

from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.MAX_USERNAME_LENGTH,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя может содержать только латинские '
                'буквы, цифры и символы'
            )
        ]
    )
    email = serializers.EmailField(
        max_length=settings.MAX_EMAIL_LENGTH,
        required=True
    )

    def validate_username(self, username):
        if username == settings.FORBIDDEN_USERNAME:
            raise serializers.ValidationError(
                f'Имя пользователя "{settings.FORBIDDEN_USERNAME}" '
                f'не разрешено.'
            )
        return username


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.MAX_USERNAME_LENGTH,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=settings.CONFIRMATION_CODE_LENGTH,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='Код подтверждения должен состоять только из цифр'
            )
        ]

    )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field="username")

    class Meta:
        fields = "__all__"
        read_only_fields = ["review"]
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field="username")

    class Meta:
        fields = "__all__"
        read_only_fields = ["title_id"]
        model = Review
        validators = (
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=("author", "title_id"),
                message="You already reviewed this title.",
            ),
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "slug")


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ("name", "slug")


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

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
    id = serializers.IntegerField(read_only=True)
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="slug"
    )
    genre = serializers.SlugRelatedField(
        many=True, queryset=Genre.objects.all(), slug_field="slug"
    )

    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "description",
            "genre",
            "category",
        )


# class TitleSerializer(serializers.ModelSerializer):
#     category = serializers.SlugRelatedField(
#         queryset=Category.objects.all(), write_only=True, slug_field="slug"
#     )
#     genre = serializers.SlugRelatedField(
#         queryset=Genre.objects.all(), many=True, write_only=True, slug_field="slug"
#     )

#     class Meta:
#         model = Title
#         fields = "__all__"

#     def to_representation(self, instance):
#         ret = super().to_representation(instance)
#         ret["category"] = CategorySerializer(instance.category).data
#         ret["genre"] = GenreSerializer(instance.genre.all(), many=True).data
#         return ret
