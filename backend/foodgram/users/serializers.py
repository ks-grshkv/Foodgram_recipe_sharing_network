from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User, Subscription
from recipes.models import Recipy
from api.image_serializer import Base64ImageField
from django.shortcuts import get_object_or_404


class UserSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для работы с пользователями.
    Используется во время создания, получения списка пользователей,
    а также получения информации о конкретном пользователе.
    """
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True,
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        model = User

    def get_is_subscribed(self, instance):
        try:
            user = self.context['request'].user
            if user.is_anonymous:
                return False
            return Subscription.objects.filter(
                user=user, author=instance
            ).exists()
        except KeyError:
            return False


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
        if (
            (data.get('email') is None)
            or (data.get('password') is None)
        ):
            raise serializers.ValidationError('Отправьте не пустой email')
        return data


class UpdatePasswordSerializer(serializers.ModelSerializer):
    """
    Сериализатор данных для обновления пароля.
    """
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    class Meta:
        fields = ('new_password', 'current_password')
        model = User

    def validate(self, data):
        if (
            (data.get('password') is None)
            or (data.get('new_password') is None)
        ):
            raise serializers.ValidationError('Пароль не может быть пустым')
        return data


class RecipyReadMinimalSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткой информации о рецепте.
    Используется во вложенных рецептах (например, в users/subscriptions).
    """
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time',)
        model = Recipy


class UserFollowWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользователя со вложенными рецептами.
    Используется для создания подписок.
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'recipes_count',
            'recipes',
            'is_subscribed'
        )
        model = Subscription

    def identify_author(self, instance):
        return get_object_or_404(User, id=self.context['kwargs'].get('id'))

    def get_recipes(self, instance):
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            serializer = RecipyReadMinimalSerializer(
                self.identify_author(
                    instance).recipes.all()[:int(recipes_limit)],
                many=True
            )
        else:
            serializer = RecipyReadMinimalSerializer(
                self.identify_author(instance).recipes.all(),
                many=True
            )
        return serializer.data

    def validate(self, data):
        user = self.context['request'].user.id
        author = self.context['kwargs'].get('id')
        if int(user) == int(author):
            raise serializers.ValidationError(
                'Нельзя подписаться на себя!'
            )

        if Subscription.objects.filter(user__id=user, author__id=author):
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя!'
            )
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        author = self.identify_author(validated_data)
        new_subscription = Subscription(
            user=user,
            author=author
        )
        new_subscription.save()
        return new_subscription

    def get_id(self, instance):
        return self.identify_author(instance).id

    def get_username(self, instance):
        return self.identify_author(instance).username

    def get_first_name(self, instance):
        return self.identify_author(instance).first_name

    def get_last_name(self, instance):
        return self.identify_author(instance).last_name

    def get_email(self, instance):
        return self.identify_author(instance).email

    def get_recipes_count(self, instance):
        return self.identify_author(instance).recipes.count()

    def get_is_subscribed(self, instance):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user,
            author=self.identify_author(instance)
        ).exists()


class UserFollowReadSerializer(UserFollowWriteSerializer):
    """
    Сериализатор для пользователя со вложенными рецептами.
    Используется для отображения существующих подписок
    Текущего пользователя.
    """

    def identify_author(self, instance):
        return instance.author
