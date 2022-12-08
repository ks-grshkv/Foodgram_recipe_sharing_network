from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.db import transaction
from recipes.models import (Favorite, Ingredient, IngredientsToRecipe, Recipy,
                            ShoppingCart, ShoppingCartItem, Tag)
from users.serializers import UserSerializer

from .image_serializer import Base64ImageField


class IngredientPrimaryKeyRelatedField(serializers.RelatedField):
    """
    Помогает вывести правильный id ингредиента,
    а не записи в связной модели IngredientsToRecipe.
    """
    def to_representation(self, instance):
        ingredient_in_recipy = get_object_or_404(
            IngredientsToRecipe,
            id=instance
        )
        return ingredient_in_recipy.ingredient.id

    def to_internal_value(self, value):
        return value


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тегов.
    """
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class TagsPrimaryKeyRelatedField(serializers.RelatedField):
    """
    Помогает вывести не просто id тега, но и всю его
    развернутую информацию.
    """
    def to_representation(self, instance):
        serializer = TagSerializer(instance)
        return serializer.data

    def to_internal_value(self, value):
        return value


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингредиентов.
    """
    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientsToRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор связной модели для ингредиентов в рецепте.
    """
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    id = IngredientPrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        fields = ('id', 'amount', 'name', 'measurement_unit')
        model = IngredientsToRecipe

    def get_measurement_unit(self, instance):
        ingredient = Ingredient.objects.get(id=instance.ingredient_id)
        return ingredient.measurement_unit

    def get_name(self, instance):
        ingredient = Ingredient.objects.get(id=instance.ingredient_id)
        return ingredient.name


class RecipyReadSerializer(serializers.ModelSerializer):
    """
    Чтение рецепта.
    """
    author = UserSerializer()
    ingredients = IngredientsToRecipeSerializer(
        many=True,
        source='recipy_with_ingredients'
    )
    tags = TagSerializer(
        many=True
    )
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Recipy

    def get_is_favorited(self, instance):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipy=instance).exists()

    def get_is_in_shopping_cart(self, instance):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipy=instance).exists()


class RecipyWriteSerializer(serializers.ModelSerializer):
    """
    Создание и редактирование рецепта.
    """
    author = serializers.SerializerMethodField()
    ingredients = IngredientsToRecipeSerializer(
        many=True,
        source='recipy_with_ingredients'
    )
    tags = TagsPrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Recipy

    def create_ingredients(self, ingredients, recipy):
        ingredient_list = []
        IngredientsToRecipe.objects.filter(recipy=recipy).delete()
        for ingredient in ingredients:
            ingredient_obj = get_object_or_404(Ingredient, id=ingredient['id'])
            ingredient_list.append(
                IngredientsToRecipe(
                    recipy=recipy, ingredient=ingredient_obj,
                    amount=ingredient['amount'])
                )
        IngredientsToRecipe.objects.bulk_create(ingredient_list)

    def get_is_favorited(self, instance):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipy=instance).exists()

    def get_author(self, *args):
        serializer = UserSerializer(self.context['request'].user)
        return serializer.data

    def get_is_in_shopping_cart(self, instance):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipy=instance).exists()

    def create_tags(self, tags, recipy):
        current_tags = recipy.tags.all()
        for current_tag in current_tags:
            recipy.tags.remove(current_tag)
        for tag in tags:
            recipy.tags.add(tag)

    @transaction.atomic
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients = validated_data.pop('recipy_with_ingredients')
        instance = super().update(instance, validated_data)
        self.create_tags(tags_data, instance)
        self.create_ingredients(ingredients, instance)
        return instance

    @transaction.atomic
    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients = validated_data.pop('recipy_with_ingredients')
        validated_data['author'] = self.context['request'].user
        instance = super().create(validated_data)
        self.create_tags(tags_data, instance)
        self.create_ingredients(ingredients, instance)
        return instance


class ShoppingCartItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор объектов в списке покупок.
    """
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        fields = ('ingredient', 'amount', 'measurement_unit')
        model = ShoppingCartItem

    def get_measurement_unit(self, instance):
        return instance.ingredient.measurement_unit


class ShoppingCartReadSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = ShoppingCart
