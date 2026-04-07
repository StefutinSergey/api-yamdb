from django.conf import settings
from django.core.validators import RegexValidator
from rest_framework import serializers

USERNAME_VALIDATION_MESSAGE = "Имя пользователя может содержать"
" только латинские буквы, цифры и символы"


def validate_username(username):
    if username == settings.USER_PAGE_URL:
        raise serializers.ValidationError(
            f'Имя пользователя "{settings.USER_PAGE_URL}" ' f"не разрешено."
        )
    validator = RegexValidator(
        regex=settings.USERNAME_REGEX,
        message=USERNAME_VALIDATION_MESSAGE,
    )
    validator(username)
    return username
