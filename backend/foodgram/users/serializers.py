from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from .models import User, Subscription


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
            'id',
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


class SubscriptionSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Subscription

    def get_is_subscribed(self, instance):
        request = self.context.get('request')
        user = self.context['request'.user]
        return (not (request is None)
                and (instance.author.filter(user=user).exists()))
    