import django_filters as filters

from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    """
    Фильтрация по нескольким тегам, с использованием
    поля slug объекта tag.
    Для не содержащихся в модели полей реализованы кастомные фильтры.
    """

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.CharFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.CharFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags']

    def filter_is_favorited(filterobj, queryset, field_name, value):
        if not value:
            return queryset
        return Recipe.objects.filter(favorite__user=filterobj.request.user)

    def filter_is_in_shopping_cart(filterobj, queryset, field_name, value):
        if not value:
            return queryset
        return Recipe.objects.filter(
            shopping_cart__user=filterobj.request.user
        )
