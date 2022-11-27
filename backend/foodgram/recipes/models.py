from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name='Тег')
    slug = models.SlugField(unique=True, max_length=50)
    color = models.CharField(max_length=7, default="#ffffff")

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    title = models.CharField(max_length=256)
    unit = models.CharField(max_length=256)


class Recipy(models.Model):
    name = models.CharField(max_length=256)
    text = models.TextField()
    tag = models.ManyToManyField(Tag, blank=True)
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/',
        null=True,
        blank=True)
    cooking_time = models.IntegerField(null=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes')
    ingredients = models.ManyToManyField(Ingredient, blank=True)

    filter_horizontal = ('tag')


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        blank=True,
        null=True,
        verbose_name='Автор')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        blank=True,
        null=True,
        verbose_name='Пользователь')


class Favorite(models.Model):
    pass


class ShoppingCart(models.Model):
    pass