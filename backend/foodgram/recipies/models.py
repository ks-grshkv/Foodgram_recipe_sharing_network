from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    title = models.CharField(max_length=256)


class Recipy(models.Model):
    title = models.CharField(max_length=256)
    text = models.TextField()
    tag = models.ManyToManyField(Tag, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipies')


class Ingredient(models.Model):
    title = models.CharField(max_length=256)
    unit = models.CharField(max_length=256)
