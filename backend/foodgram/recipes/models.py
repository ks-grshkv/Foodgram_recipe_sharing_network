from colorfield.fields import ColorField
from django.db import models
from django.utils.text import slugify

from users.models import User


class Tag(models.Model):
    """
    Модель тегов для классификации и фильтрации рецептов.
    """
    name = models.CharField(
        verbose_name='Название тега',
        max_length=256,
        unique=True,
        null=False,
        blank=False
    )
    color = ColorField(
        verbose_name='Цвет тега',
        default='#FF0000',
        unique=True,
        null=False,
        blank=False
    )
    slug = models.SlugField(
        verbose_name='Слаг тега',
        unique=True,
        max_length=50,
        null=False,
        blank=False
    )

    def save(self, *args, **kwargs):
        """
        На всякий случай делает slugify поля slug
        перед сохранением в БД.
        """
        self.slug = slugify(self.slug)
        super(Tag, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        unique=True,
        null=False,
        blank=False)
    measurement_unit = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        verbose_name='Единицы')

    class Meta:
        ordering = ('-name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """
    Модель рецептов. Property favorited_count показывает
    общее количество раз, когда рецепт добавили в избранное.
    """
    name = models.CharField(
        max_length=256,
        null=False,
        blank=False)
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
        null=False,
        blank=False
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
        return Favorite.objects.filter(recipe=self).count()


class IngredientsToRecipe(models.Model):
    """
    Смежная модель для свящи Ингредиентов и Рецептов.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredients_to_recipe',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        verbose_name='Количество'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_with_ingredients',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('-recipe',)
        verbose_name = 'Ингредиенты к рецептам'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.recipe} <- {self.ingredient.name}'


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
        Recipe,
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
        return f'{self.user} likes {self.recipe}'


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
        Recipe,
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
        return f'{self.user} buys {self.recipe}'
