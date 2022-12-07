import django_filters as filters

from recipes.models import Recipy, Tag


class RecipyFilter(filters.FilterSet):
    """
    Фильтрация по нескольким тегам, с использованием
    поля slug объекта tag.
    """
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipy
        fields = ['tags',]
