import django_filters as filters

from recipes.models import Recipe, Tag, Favorite, ShoppingCart


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

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.user = self.request.user
        super(RecipeFilter, self).__init__(*args, **kwargs)

    def filter_is_favorited(filterobj, queryset, field_name, value):
        recipes = [
                x.recipe.id for x in Favorite.objects.all()
                if x.user == filterobj.user
            ]
        queryset = queryset.filter(id__in=recipes)
        return queryset

    def filter_is_in_shopping_cart(filterobj, queryset, field_name, value):
        recipes = [
                x.recipe.id for x in ShoppingCart.objects.all()
                if x.user == filterobj.user
            ]
        queryset = queryset.filter(id__in=recipes)
        return queryset

    class Meta:
        model = Recipe
        fields = ['tags']
