from recipes.models import Recipy, Tag
import django_filters as filters
# from rest_framework import filters


class RecipyFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipy
        fields = ['tags',]
