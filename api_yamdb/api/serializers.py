from rest_framework import serializers
from django.contrib.auth import get_user_model


from reviews.models import Comment, Review, Category, Title, Genre

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
import re

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" не разрешено.')
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Имя пользователя может'
                ' содержать только буквы, цифры и символы'
            )
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def validate_role(self, value):
        allowed_roles = ['user', 'moderator', 'admin']
        if value not in allowed_roles:
            raise serializers.ValidationError('Недопустимая роль')
        return value

    def validate_email(self, value):
        if len(value) > 254:
            raise serializers.ValidationError(
                'Email не может быть длиннее 254 символов.'
            )
        if self.instance is None:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    'Пользователь с таким email уже существует.'
                )
        else:
            if User.objects.exclude(
                pk=self.instance.pk
            ).filter(email=value).exists():
                raise serializers.ValidationError(
                    'Пользователь с таким email уже существует.'
                )
        return value


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

        title = get_object_or_404(Title, id=request.parser_context.get('kwargs', {})['title_id'])
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
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
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
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
        )

    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['category'] = CategorySerializer(instance.category).data
        ret['genre'] = GenreSerializer(instance.genre.all(), many=True).data
        return ret

    def validate_role(self, value):
        allowed_roles = ['user', 'moderator', 'admin']
        if value not in allowed_roles:
            raise serializers.ValidationError('Недопустимая роль')
        return value
