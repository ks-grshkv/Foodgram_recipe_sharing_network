from django.db import models
from colorfield.fields import ColorField
from users.models import User


class Tag(models.Model):
    """
    Модель тегов для классификации и фильтрации рецептов.
    """
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)
    color = ColorField(default='#FF0000')

    class Meta:
        ordering = ('-name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

    # def save(self):
    #     pass


class Ingredient(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    measurement_unit = models.CharField(max_length=256, verbose_name='Единицы')

    class Meta:
        ordering = ('-name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipy(models.Model):
    """
    Модель рецептов. Property favorited_count показывает
    общее количество раз, когда рецепт добавили в избранное.
    """
    name = models.CharField(max_length=256)
    text = models.TextField(
        null=False,
        blank=False,
        verbose_name='Текст рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        verbose_name='Теги'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/media/',
        null=True,
        blank=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        null=False,
        blank=False,
        verbose_name='Время приготовления, мин'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsToRecipe',
        verbose_name='Ингредиенты'
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
    """
    Смежная модель для свящи Ингредиентов и Рецептов.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredients_to_recipy',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        verbose_name='Количество'
    )
    recipe = models.ForeignKey(
        Recipy,
        related_name='recipy_with_ingredients',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('-recipe',)
        verbose_name = 'Ингредиенты к рецептам'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.recipy} <- {self.ingredient.name}'


class Favorite(models.Model):
    """
    Модель для добавления рецептов в избранное.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        blank=True,
        null=True,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipy,
        related_name='favorite',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Лайкнул рецепт'
    )

    class Meta:
        ordering = ('-user',)
        verbose_name = 'Добавление в избранное'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user} likes {self.recipy}'


class ShoppingCart(models.Model):
    """
    Модель для добавления рецептов в список покупок.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        blank=True,
        null=True,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipy,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Добавил в корзину рецепт'
    )

    class Meta:
        ordering = ('-user',)
        verbose_name = 'Добавление рецептов в список покупок'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user} buys {self.recipy}'


class ShoppingCartItem(models.Model):
    """
    Модель айтема в списке покупок.
    """
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
