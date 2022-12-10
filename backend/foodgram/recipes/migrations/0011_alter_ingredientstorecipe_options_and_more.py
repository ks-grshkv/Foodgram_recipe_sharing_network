# Generated by Django 4.1.3 on 2022-12-08 15:52

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_alter_favorite_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientstorecipe',
            options={'ordering': ('-recipe',), 'verbose_name': 'Ингредиенты к рецептам', 'verbose_name_plural': 'Ингредиенты к рецептам'},
        ),
        migrations.RenameField(
            model_name='favorite',
            old_name='recipy',
            new_name='recipe',
        ),
        migrations.RenameField(
            model_name='ingredientstorecipe',
            old_name='recipy',
            new_name='recipe',
        ),
        migrations.RenameField(
            model_name='shoppingcart',
            old_name='recipy',
            new_name='recipe',
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=18, samples=None),
        ),
    ]