from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.db import transaction
from api.image_serializer import Base64ImageField
from recipes.models import Recipy

from .models import Subscription, User


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
        if not self.context:
            return False
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user, author=instance
        ).exists()


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


class UserPrimaryKeyRelatedField(serializers.RelatedField):
    """
    Помогает вывести правильный id ингредиента,
    а не записи в связной модели IngredientsToRecipe.
    """
    def to_representation(self, instance):
        print('AAAA 108 ser', instance)
        author = get_object_or_404(Subscription, id=instance).author
        return author.id

    def to_internal_value(self, value):
        print('AAAA 116 ser', value)
        return value


class UserFollowWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользователя со вложенными рецептами.
    Используется для создания подписок.
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    # id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    # username = serializers.SerializerMethodField()
    # email = serializers.SerializerMethodField()
    # last_name = serializers.SerializerMethodField()
    # first_name = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            # 'username',
            # 'email',
            # 'first_name',
            # 'last_name',
            'recipes_count',
            'recipes',
            'is_subscribed'
        )
        model = Subscription

    def identify_author(self, instance):
        print('133 ser')
        return get_object_or_404(User, id=self.context['kwargs'].get('id'))

    def get_recipes(self, instance):
        print('135 ser')
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
        print('152 ser')
        user = self.context['request'].user
        author = get_object_or_404(
            User,
            id=self.context['kwargs'].get('id')
        )
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя!'
            )

        if Subscription.objects.filter(user=user, author=author):
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя!'
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        print('169 ser')
        user = self.context['request'].user
        author = self.identify_author(validated_data)
        new_subscription = Subscription(
            user=user,
            author=author
        )
        new_subscription.save()
        return new_subscription

    # def get_id(self, instance):
    #     return self.identify_author(instance).id

    # def get_username(self, instance):
    #     return self.identify_author(instance).username

    # def get_first_name(self, instance):
    #     return self.identify_author(instance).first_name

    # def get_last_name(self, instance):
    #     return self.identify_author(instance).last_name

    # def get_email(self, instance):
    #     return self.identify_author(instance).email

    def get_recipes_count(self, instance):
        print('194 ser')
        return self.identify_author(instance).recipes.count()

    def get_is_subscribed(self, instance):
        print('197 ser')
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
    id = UserPrimaryKeyRelatedField(queryset=User.objects.all())
    # id = UserSerializer()

    def identify_author(self, instance):
        print('213 ser')
        return instance.author
