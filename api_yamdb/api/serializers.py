from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title

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
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        request = self.context.get('request')
        if request.method != 'POST':
            return data

        title = get_object_or_404(
            Title,
            id=request.parser_context.get('kwargs', {}).get('title_id')
        )
        if Review.objects.filter(
            author=request.user, title_id=title.id
        ).exists():
            raise serializers.ValidationError(
                f'"{title.name}" already reviewed by {request.user.username}'
            )
        return data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre',
            'category', 'rating'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        many=True, queryset=Genre.objects.all(), slug_field='slug'
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )