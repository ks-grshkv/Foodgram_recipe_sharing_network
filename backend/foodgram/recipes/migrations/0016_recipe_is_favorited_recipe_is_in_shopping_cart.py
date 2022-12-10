# Generated by Django 4.1.3 on 2022-12-09 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0015_alter_tag_color_alter_tag_name_alter_tag_slug_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='is_favorited',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='is_in_shopping_cart',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]