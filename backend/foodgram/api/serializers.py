from recipes.models import Recipy, Tag, Ingredient, ShoppingCart, Favorite, IngredientsToRecipe, ShoppingCartItem
from users.serializers import UserSerializer
from users.models import Subscription
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField, PrimaryKeyRelatedField
from .image_serializer import Base64ImageField


# class AddIngredientSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
#     amount = serializers.IntegerField()

#     class Meta:
#         model = IngredientsToRecipe
#         fields = ("id", "amount")

class IngredientPrimaryKeyRelatedField(serializers.RelatedField):
    def to_representation(self, instance):
        print('FFFFFFF11111F', self, instance)
        ingredient_in_recipy = get_object_or_404(IngredientsToRecipe, id=instance)

        return ingredient_in_recipy.ingredient.id
    
    def to_internal_value(self, value):
        print('FFFFFFF22222F', self,  value)
        return value


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient
        # exclude = ('id',)


class IngredientsToRecipeReadSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'amount', 'name', 'measurement_unit')
        model = IngredientsToRecipe

    def get_id(self, instance):
        return instance.ingredient.id

    def get_measurement_unit(self, instance):
        ingredient = Ingredient.objects.get(id=instance.ingredient_id)
        return ingredient.measurement_unit

    def get_name(self, instance):
        ingredient = Ingredient.objects.get(id=instance.ingredient_id)
        return ingredient.name


class IngredientsToRecipeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    # id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    id = IngredientPrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    # id = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'amount', 'name', 'measurement_unit')
        model = IngredientsToRecipe
    
    # def get_id(self, instance):
    #     return instance.ingredient.id

    def get_measurement_unit(self, instance):
        ingredient = Ingredient.objects.get(id=instance.ingredient_id)
        return ingredient.measurement_unit

    def get_name(self, instance):
        ingredient = Ingredient.objects.get(id=instance.ingredient_id)
        return ingredient.name


class RecipyReadSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ingredients = IngredientsToRecipeReadSerializer(
        many=True,
        source='recipy_with_ingredients'
    )
    tags = TagSerializer(
        many=True
    )
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Recipy

    def get_author(self, instance):
        serializer = UserSerializer(instance.author)
        return serializer.data

    def get_is_favorite(self, instance):
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
    author = serializers.SerializerMethodField()
    ingredients = IngredientsToRecipeSerializer(
        many=True,
        source='recipy_with_ingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Recipy

    def create_ingredients(self, ingredients, recipy):
        IngredientsToRecipe.objects.filter(recipy=recipy).delete()
        for ingredient in ingredients:
            print('aAAAAAAAA INGREDIENT', ingredient)
            ingredient_obj = get_object_or_404(Ingredient, id=ingredient['id'])
            IngredientsToRecipe.objects.create(
                recipy=recipy, ingredient=ingredient_obj,
                amount=ingredient['amount']
            )
        print('FINISH INGREDIENTS')

    def get_is_favorite(self, instance):
        return False
    
    def get_author(self, *args):
        serializer = UserSerializer(self.context['request'].user)
        return serializer.data

    def get_is_in_shopping_cart(self, instance):
        return False

    def create_tags(self, tags, recipy):
        current_tags = recipy.tags.all()
        print('CREATE TAGSS', tags)
        for current_tag in current_tags:
            print('TAG', current_tag)
            recipy.tags.remove(current_tag)
        for tag in tags:
            print('TAG', tag)
            recipy.tags.add(tag)
        print('FINISH TAGS')
    
    def update(self, instance, validated_data):
        print('AAAAAA UPDATE')
        tags_data = validated_data.pop('tags')
        name = validated_data.get('name')
        image = validated_data.get('image')
        text = validated_data.get('text')
        cooking_time = validated_data.get('cooking_time')
        ingredients = validated_data.pop('recipy_with_ingredients')
        print('AAAAAA DATA POPPED')
        recipy = get_object_or_404(Recipy, id=instance.id)
        recipy.name = name
        recipy.image = image
        recipy.text = text
        recipy.cooking_time = cooking_time
        self.create_tags(tags_data, recipy)
        print('AAAAAA CREATIN INGR')
        self.create_ingredients(ingredients, recipy)
        print('SAVING RECIPY.....')
        recipy.save()
        print('FINISH UPDATE')
        return recipy
    
    def create(self, validated_data):
        print('AAAAAA CREATE')
        tags_data = validated_data.pop('tags')
        name = validated_data.get('name')
        image = validated_data.get('image')
        text = validated_data.get('text')
        cooking_time = validated_data.get('cooking_time')
        ingredients = validated_data.pop('recipy_with_ingredients')
        recipy = Recipy.objects.create(
            author=self.context['request'].user,
            name=name,
            image=image,
            text=text,
            cooking_time=cooking_time,
        )
        print('AAAAAA CREATIN TAGS')
        self.create_tags(tags_data, recipy)
        print('AAAAAA CREATIN INGR')
        self.create_ingredients(ingredients, recipy)
        print('AAAAAA FINISH CREATE SRIALIZER')
        return recipy


class ShoppingCartItemSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(max_length=200)
    # amount = serializers.IntegerField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        fields = ('ingredient', 'amount', 'measurement_unit')
        model = ShoppingCartItem

    def get_measurement_unit(self, instance):
        return instance.ingredient.measurement_unit

    # def create(self, **validated_data):
    #     name = validated_data.pop('name')
    #     amount = validated_data.pop('amount')
    #     return None


class ShoppingCartReadSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = ShoppingCart

    def get_file(self, instance):
        return None


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Favorite



