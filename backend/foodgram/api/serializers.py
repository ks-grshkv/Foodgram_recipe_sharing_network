from recipes.models import Recipy, Tag, Ingredient, ShoppingCart, Favorite, IngredientsToRecipe
from users.models import User
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class RecipySerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        # read_only=True
    )
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(),
        slug_field='name',
        many=True,
        # read_only=True
    )
    ingredients = serializers.SlugRelatedField(
        queryset=Ingredient.objects.all(),
        slug_field='name',
        many=True,
        # read_only=True
    )
    image = serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True)
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Recipy

    def get_is_favorite(self, instance):
        # request = self.context.get('request')
        user = self.context['request'].user
        print(instance)
        return Favorite.objects.filter(user=user, recipy=instance).exists()
    
    def get_is_in_shopping_cart(self, instance):
        user = self.context['request'].user
        return ShoppingCart.objects.filter(user=user, recipy=instance).exists()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient
        # exclude = ('id',)


class IngredientsToRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('amount',)
        model = IngredientsToRecipe


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = ShoppingCart


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Favorite


class SlugToModelTagRelatedField(SlugRelatedField):
    def to_representation(self, instance):
        serializer = TagSerializer(instance)
        return serializer.data
