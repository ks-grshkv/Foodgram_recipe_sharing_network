# Generated by Django 4.1.3 on 2022-12-02 21:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_recipy_is_favorite'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipy',
            name='is_favorite',
        ),
    ]