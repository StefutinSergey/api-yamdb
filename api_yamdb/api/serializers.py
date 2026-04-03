from rest_framework import serializers
from django.contrib.auth import get_user_model
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
                'Имя пользователя может содержать только буквы, цифры и символы'
            )
        return value

    def validate_email(self, value):
        if len(value) > 254:
            raise serializers.ValidationError(
                'Email не может быть длинее 254 символов.'
            )
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
