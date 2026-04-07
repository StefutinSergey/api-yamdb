from rest_framework import serializers
from reviews.validators import validate_username

class UsernameValidationMixin:
    def validate_username(self, value):
        return validate_username(value)
