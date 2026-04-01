from rest_framework import serializers
<<<<<<< feature/thirddeveloper
from rest_framework.validators import UniqueTogetherValidator 

from reviews.models import Comment, Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        read_only_fields = ['review']
        model = Comment
        validators = ( 
            UniqueTogetherValidator( 
                queryset=Comment.objects.all(),
                fields=('author', 'title_id'),
                message='You already reviewed this title.',
            ),
        )
=======
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" не разрешено.')
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        read_only_fields = ('role',)
>>>>>>> develop
