from recipes.models import Recipy, Tag, Ingredient, ShoppingCart, Favorite
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class RecipySerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    tag = TagSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Recipy


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient
        # exclude = ('id',)


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class SlugToModelTagRelatedField(SlugRelatedField):
    def to_representation(self, instance):
        serializer = TagSerializer(instance)
        return serializer.data
