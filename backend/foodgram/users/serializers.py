from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from .models import User, Subscription
from recipes.models import Recipy
from api.image_serializer import Base64ImageField


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
        """
        Проверяем, что пароль и email не пустые
        """
        if (
            (data.get('email') is None)
            or (data.get('password') is None)
        ):
            raise serializers.ValidationError('Отправьте не пустой email')
        return data


class UpdatePasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    class Meta:
        fields = ('new_password', 'current_password')
        model = User


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='id', read_only='True')
    author = serializers.SlugRelatedField(slug_field='id', read_only='True')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Subscription

        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=['author', 'user']
            )
        ]

    def get_is_subscribed(self, instance):
        user = instance.user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user, author=instance.author
        ).exists()


class RecipyReadMinimalSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        fields = ('name', 'text', 'image', 'cooking_time',)
        model = Recipy


class UserWithRecipesSerializer(serializers.ModelSerializer):
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

    def get_recipes(self, instance):
        serializer = RecipyReadMinimalSerializer(
            instance.author.recipes.all(),
            many=True
        )
        return serializer.data

    def get_id(self, instance):
        return instance.author.id

    def get_username(self, instance):
        return instance.author.username

    def get_first_name(self, instance):
        return instance.author.first_name

    def get_last_name(self, instance):
        return instance.author.last_name

    def get_email(self, instance):
        return instance.author.email

    def get_recipes_count(self, instance):
        return instance.author.recipes.count()

    def get_is_subscribed(self, instance):
        user = instance.user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user,
            author=instance.author
        ).exists()
