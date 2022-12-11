from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.db import transaction
from api.image_serializer import Base64ImageField
from recipes.models import Recipe, ShoppingCart, Favorite

from .models import Subscription, User


class UserSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для работы с пользователями.
    Используется во время создания, получения списка пользователей,
    а также получения информации о конкретном пользователе.
    """
    username = serializers.CharField(
        max_length=100,
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True,
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True
    )
    password = serializers.CharField(
        min_length=8,
        max_length=100,
        write_only=True
    )

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        fields = (
            'id',
            'username',
            'email',
            'password',
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
        if len(User.objects.filter(email=data.get('email'))) == 0:
            raise serializers.ValidationError('Проверьте правильность email-a')
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


class RecipeReadMinimalSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткой информации о рецепте.
    Используется во вложенных рецептах (например, в users/subscriptions),
    а также при добавлении в избранное или список покупок.
    """
    image = Base64ImageField(max_length=None, use_url=True, read_only=True)
    name = serializers.CharField(read_only=True)
    cooking_time = serializers.CharField(read_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time',)
        model = Recipe

    def validate(self, data):
        user = self.context['request'].user
        recipe = get_object_or_404(
            Recipe,
            id=self.context['kwargs'].get('pk')
        )
        if ShoppingCart.objects.filter(user=user, recipe=recipe):
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок!'
            )
        if Favorite.objects.filter(user=user, recipe=recipe):
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное!'
            )
        data['recipe'] = recipe
        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Определяем action - добавление в избранное или в список покупок
        и проводим соответствующие операции с БД. Возвращаем данные
        добавленного рецепта.
        """
        recipe = validated_data.pop('recipe')
        if self.context['action'] == 'favorite':
            new_favorite = Favorite(
                user=self.context['request'].user,
                recipe=recipe
            )
            new_favorite.save()

        if self.context['action'] == 'shopping_cart':
            new_cart_item = ShoppingCart(
                user=self.context['request'].user,
                recipe=recipe
            )
            new_cart_item.save()
        return recipe


class UserFollowWriteSerializer(UserSerializer):
    """
    Сериализатор для пользователя со вложенными рецептами.
    Используется для создания подписок.
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    email = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)

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
        model = User

    def identify_author(self, instance):
        return get_object_or_404(User, id=self.context['kwargs'].get('id'))

    def get_recipes(self, instance):
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            serializer = RecipeReadMinimalSerializer(
                self.identify_author(
                    instance).recipes.all()[:int(recipes_limit)],
                many=True
            )
        else:
            serializer = RecipeReadMinimalSerializer(
                self.identify_author(instance).recipes.all(),
                many=True
            )
        return serializer.data

    def validate(self, data):
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
        data['user'] = user
        data['author'] = author
        return data

    @transaction.atomic
    def create(self, validated_data):
        user = validated_data.pop('user')
        author = self.identify_author(validated_data)
        new_subscription = Subscription(
            user=user,
            author=author
        )
        new_subscription.save()
        return author

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
        return instance
