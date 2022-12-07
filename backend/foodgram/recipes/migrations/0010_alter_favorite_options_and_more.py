# Generated by Django 4.1.3 on 2022-12-06 20:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0009_alter_ingredient_options_alter_recipy_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ('-user',), 'verbose_name': 'Добавление в избранное', 'verbose_name_plural': 'Добавление в избранное'},
        ),
        migrations.AlterModelOptions(
            name='ingredientstorecipe',
            options={'ordering': ('-recipy',), 'verbose_name': 'Ингредиенты к рецептам', 'verbose_name_plural': 'Ингредиенты к рецептам'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'ordering': ('-user',), 'verbose_name': 'Добавление рецептов в список покупок', 'verbose_name_plural': 'Добавление рецептов в список покупок'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcartitem',
            options={'ordering': ('-cart',), 'verbose_name': 'Список покупок', 'verbose_name_plural': 'Список покупок'},
        ),
        migrations.AlterField(
            model_name='favorite',
            name='recipy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to='recipes.recipy', verbose_name='Лайкнул рецепт'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=256, verbose_name='Единицы'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=256, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='ingredientstorecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipy',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='recipy',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(verbose_name='Время приготовления, мин'),
        ),
        migrations.AlterField(
            model_name='recipy',
            name='ingredients',
            field=models.ManyToManyField(through='recipes.IngredientsToRecipe', to='recipes.ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AlterField(
            model_name='recipy',
            name='tags',
            field=models.ManyToManyField(blank=True, to='recipes.tag', verbose_name='Теги'),
        ),
        migrations.AlterField(
            model_name='recipy',
            name='text',
            field=models.TextField(verbose_name='Текст рецепта'),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='recipy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to='recipes.recipy', verbose_name='Добавил в корзину рецепт'),
        ),
    ]