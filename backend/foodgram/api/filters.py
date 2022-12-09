import django_filters as filters
from rest_framework import filters as filtering

from recipes.models import Recipe, Tag


CHOICES = (
    (1, 'True'),
    (0, 'False')
)


class RecipeFilter(filters.FilterSet):
    """
    Фильтрация по нескольким тегам, с использованием
    поля slug объекта tag.
    """
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    # is_favorited = filters.CharFilter( method='filter_not_empty',
    # )
    # is_in_shopping_cart = filters.ChoiceFilter(
    #     choices=CHOICES, method='filter_not_empty')

    # def filter_not_empty(queryset, name, value, *kwargs):
    #     print('aaaaAAAAAA', queryset)
    #     return queryset.filter(a=a)

    class Meta:
        model = Recipe
        fields = ['tags']


class CustomSearchFilter(filtering.SearchFilter):
    def get_search_fields(self, view, request):
        if request.query_params.get('is_favorited'):
            return ['title']
        return super().get_search_fields(view, request)
