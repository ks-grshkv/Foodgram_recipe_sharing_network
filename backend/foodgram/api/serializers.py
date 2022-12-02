from recipes.models import Recipy, Tag, Ingredient, ShoppingCart, Favorite, IngredientsToRecipe
from users.models import User
from users.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField, PrimaryKeyRelatedField


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsToRecipe
        fields = ("id", "amount")


class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension
        

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient
        # exclude = ('id',)


class IngredientsToRecipeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'amount', 'name', 'measurement_unit')
        model = IngredientsToRecipe

    def get_id(self, instance):
        return instance.ingredient_id

    def get_measurement_unit(self, instance):
        ingredient = Ingredient.objects.get(id=instance.ingredient_id)
        return ingredient.measurement_unit

    def get_name(self, instance):
        ingredient = Ingredient.objects.get(id=instance.ingredient_id)
        return ingredient.name


class RecipyReadSerializer(serializers.ModelSerializer):
    # author = UserSerializer()
    author = serializers.SerializerMethodField()
    ingredients = IngredientsToRecipeSerializer(
        many=True,
        source='recipy_with_ingredients'
    )
    tags = TagSerializer(
        many=True
    )

    # image = serializers.ImageField(max_length=None, allow_empty_file=True, use_url=True)
    image = Base64ImageField(
        max_length=None, use_url=True,
    )
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Recipy

    def get_author(self, instance):
        serializer = UserSerializer(instance.author)
        print('AAAA', serializer.data)
        # удалить ненужное говно, сделать is_subscribed
        return serializer.data

    def get_is_favorite(self, instance):
        user = self.context['request'].user
        return Favorite.objects.filter(user=user, recipy=instance).exists()
    
    def get_is_in_shopping_cart(self, instance):
        user = self.context['request'].user
        return ShoppingCart.objects.filter(user=user, recipy=instance).exists()


class RecipyWriteSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ingredients = AddIngredientSerializer(
        many=True,
        source='recipy_with_ingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    # image = serializers.ImageField(max_length=None, allow_empty_file=True, use_url=True)
    image = Base64ImageField(
        max_length=None, use_url=True,
    )
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Recipy

    def get_is_favorite(self, instance):
        # тут какая-то параша
        print('ENTER get_is_favorite')
        user = self.context['request'].user
        return Favorite.objects.filter(user=user, recipy=instance).exists()
    
    def get_author(self, *args):
        print('ENTER get_author')
        user = self.context['request'].user
        return user

    def get_is_in_shopping_cart(self, instance):
        print('ENTER get_is_in_shopping_cart')
        user = self.context['request'].user
        return ShoppingCart.objects.filter(user=user, recipy=instance).exists()

    def create_ingredients(self, ingredients, recipy):
        print('create_ingredients')
        for ingredient in ingredients:
            IngredientsToRecipe.objects.create(
                recipy=recipy, ingredient=ingredient['id'],
                amount=ingredient['amount']
        )

    def create_tags(self, tags, recipy):
        print('create_tags')
        for tag in tags:
            recipy.tags.add(tag)
    
    def create(self, validated_data):
        print('ENTER create')
        author = self.get_author()
        print('AAAAAAAAAA', validated_data)
        tags_data = validated_data.pop('tags')
        print(tags_data)
        name = validated_data.get('name')
        image = validated_data.get('image')
        text = validated_data.get('text')
        cooking_time = validated_data.get('cooking_time')
        ingredients = validated_data.pop('recipy_with_ingredients')
        print('CREATE RECIPY')
        recipy = Recipy.objects.create(
            author=author,
            name=name,
            image=image,
            text=text,
            cooking_time=cooking_time,
        )
        self.create_tags(tags_data, recipy)
        print('CREATE TAGS DONE')
        self.create_ingredients(ingredients, recipy)
        return recipy


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
