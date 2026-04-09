from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from rest_framework import serializers

USERNAME_VALIDATION_MESSAGE = (
    "Имя пользователя может содержать только латинские "
    "буквы, цифры и символы"
)
USERNAME_REGEX_VALIDATOR = RegexValidator(
    regex=settings.USERNAME_REGEX,
    message=USERNAME_VALIDATION_MESSAGE,
)


def validate_username(username):
    if username == settings.USER_PAGE_URL:
        raise serializers.ValidationError(
            f'Логин "{settings.USER_PAGE_URL}" не разрешен.'
        )
    USERNAME_REGEX_VALIDATOR(username)
    return username


def validate_username_for_model(value):
    try:
        validate_username(value)
    except serializers.ValidationError as e:
        raise ValidationError(e.detail)
