from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)
    color = models.CharField(max_length=7, default="#ffffff")

    class Meta:
        ordering = ('-name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=256)
    measurement_unit = models.CharField(max_length=256)

    class Meta:
        ordering = ('-name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


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

    filter_horizontal = ('tags')

    class Meta:
        ordering = ('-name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    @property
    def favorited_count(self):
        return Favorite.objects.filter(recipy=self).count()


class IngredientsToRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredients_to_recipy',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField()
    recipy = models.ForeignKey(
        Recipy,
        related_name='recipy_with_ingredients',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('-recipy',)
        verbose_name = 'Ингредиенты к рецептам'
        verbose_name_plural = verbose_name


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

    class Meta:
        ordering = ('-user',)
        verbose_name = 'Добавление в избранное'
        verbose_name_plural = verbose_name


class ShoppingCart(models.Model):
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

    class Meta:
        ordering = ('-user',)
        verbose_name = 'Добавление рецептов в список покупок'
        verbose_name_plural = verbose_name


class ShoppingCartItem(models.Model):
    cart = models.ForeignKey(
        ShoppingCart,
        on_delete=models.CASCADE,
        related_name='shopping_cart_items',
        blank=True,
        null=True,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredient_to_buy',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('-cart',)
        verbose_name = 'Список покупок'
        verbose_name_plural = verbose_name
