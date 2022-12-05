from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)
    color = models.CharField(max_length=7, default="#ffffff")

    # def __str__(self):
    #     return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=256)
    measurement_unit = models.CharField(max_length=256)

    # def __str__(self):
    #     return self.name


class Recipy(models.Model):
    name = models.CharField(max_length=256)
    text = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True)
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/media/',
        null=True,
        blank=True
    )
    cooking_time = models.IntegerField(null=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsToRecipe'
    )

    # filter_horizontal = ('tag')

    def __str__(self):
        return self.name


class IngredientsToRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredients_to_recipy',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField()
    recipy = models.ForeignKey(
        Recipy,
        related_name='recipy_with_ingredients',
        on_delete=models.CASCADE
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        blank=True,
        null=True,
        verbose_name='Пользователь'
    )
    recipy = models.ForeignKey(
        Recipy,
        related_name='favorite',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )


class ShoppingCart(models.Model):
    file = models.FileField(
        verbose_name='Список покупок',
        upload_to='recipes/media/txt/',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        blank=True,
        null=True,
        verbose_name='Пользователь'
    )
    recipy = models.ForeignKey(
        Recipy,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
