from django_filters import rest_framework
from recipes.models import Recipy


class RecipyFilter(rest_framework.FilterSet):
    author = rest_framework.CharFilter(field_name='author')
    # name = rest_framework.CharFilter(
    #     field_name='name',
    #     lookup_expr='icontains'
    # )

    class Meta:
        model = Recipy
        fields = ['tags', 'is_favorite', 'author', 'is_in_shopping_cart']
