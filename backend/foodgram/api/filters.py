from recipes.models import Recipy, Tag
import django_filters as filters


class CustomFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name="tags__slug", method='filter_tags')
    # tags = filters.AllValuesMultipleFilter(
    #     field_name='tags__slug', 
    #     to_field_name='slug',
    #     lookup_expr='in',
    #     queryset=Tag.objects.all()
    # )

    class Meta:
        model = Recipy
        fields = ['tags']

    def filter_tags(self, queryset, slug, tags):
        print('AAAAAAAAAAAAA')
        return queryset.filter(tags__slug__contains=tags.split(','))



# class CustomFilter(django_filters.FilterSet):
#     tags = django_filters.AllValuesMultipleFilter(
#         field_name='tags__slug',
#         # to_field_name='slug',
#         # lookup_expr='in',
#         queryset=Tag.objects.all()
#     )

#     class Meta:
#         model = Recipy
#         fields = ['tags', ]
