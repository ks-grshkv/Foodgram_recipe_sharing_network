from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from .models import User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True,
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True
    )

    class Meta:
        fields = (
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'role'
        )
        model = User

        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=User.objects.all(),
        #         fields=['username', 'email']
        #     )
        # ]

    def validate_username(self, value):
        """
        Проверяем, что нельзя сделать юзернейм 'me'
        """
        if value == 'me':
            raise serializers.ValidationError('Задайте другой юзернейм')
        if value is None:
            raise serializers.ValidationError('Задайте не пустой юзернейм')
        return value


class GetTokenSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        max_length=254,
        required=True,
    )

    class Meta:
        fields = (
            'email',
            'password'
        )
        model = User

    def validate(self, data):
        """
        Проверяем, что пароль и email не пустые
        """
        if (
            (data.get('email') is None)
            or (data.get('password') is None)
        ):
            raise serializers.ValidationError('Отправьте не пустой email')
        return data
