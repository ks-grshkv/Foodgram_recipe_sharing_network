from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientsToRecipe, Recipe,
                            ShoppingCart, Tag)
from users.serializers import UserSerializer


class IngredientPrimaryKeyRelatedField(serializers.RelatedField):
    """
    Помогает вывести правильный id ингредиента,
    а не записи в связной модели IngredientsToRecipe.
    """
    def to_representation(self, instance):
        ingredient_in_recipe = get_object_or_404(
            IngredientsToRecipe,
            id=instance
        )
        return ingredient_in_recipe.ingredient.id

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

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Проверьте количество ингредиентов. Оно не может быть < 0'
            )
        return value

    def get_measurement_unit(self, instance):
        ingredient = Ingredient.objects.get(id=instance.ingredient_id)
        return ingredient.measurement_unit

    def get_name(self, instance):
        ingredient = Ingredient.objects.get(id=instance.ingredient_id)
        return ingredient.name


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Чтение рецепта.
    """
    author = UserSerializer()
    ingredients = IngredientsToRecipeSerializer(
        many=True,
        source='recipe_with_ingredients'
    )
    tags = TagSerializer(
        many=True
    )
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Recipe

    def get_is_favorited(self, instance):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=instance).exists()

    def get_is_in_shopping_cart(self, instance):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=instance).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Создание и редактирование рецепта.
    """
    author = serializers.SerializerMethodField()
    ingredients = IngredientsToRecipeSerializer(
        many=True,
        source='recipe_with_ingredients'
    )
    tags = TagsPrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Recipe

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError('Укажите время готовки > 1 мин.')
        return value

    def create_ingredients(self, ingredients, recipe):
        ingredient_list = []
        IngredientsToRecipe.objects.filter(recipe=recipe).delete()
        for ingredient in ingredients:
            ingredient_obj = get_object_or_404(Ingredient, id=ingredient['id'])
            ingredient_list.append(
                IngredientsToRecipe(
                    recipe=recipe, ingredient=ingredient_obj,
                    amount=ingredient['amount'])
                )
        IngredientsToRecipe.objects.bulk_create(ingredient_list)

    def get_is_favorited(self, instance):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=instance).exists()

    def get_author(self, *args):
        serializer = UserSerializer(self.context['request'].user)
        return serializer.data

    def get_is_in_shopping_cart(self, instance):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=instance).exists()

    def create_tags(self, tags, recipe):
        current_tags = recipe.tags.all()
        for current_tag in current_tags:
            recipe.tags.remove(current_tag)
        for tag in tags:
            recipe.tags.add(tag)

    @transaction.atomic
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_with_ingredients')
        instance = super().update(instance, validated_data)
        self.create_tags(tags_data, instance)
        self.create_ingredients(ingredients, instance)
        return instance

    @transaction.atomic
    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_with_ingredients')
        validated_data['author'] = self.context['request'].user
        instance = super().create(validated_data)
        self.create_tags(tags_data, instance)
        self.create_ingredients(ingredients, instance)
        return instance
