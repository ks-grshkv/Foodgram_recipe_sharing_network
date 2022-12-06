from django.http import HttpResponse
from recipes.models import (
    ShoppingCartItem,
    Recipy,
    Tag,
    Ingredient,
    ShoppingCart,
    Favorite,
    IngredientsToRecipe)
from users.serializers import RecipyReadMinimalSerializer
from http import HTTPStatus
from .serializers import (
    RecipyReadSerializer,
    RecipyWriteSerializer,
    TagSerializer,
    IngredientSerializer,
    ShoppingCartItemSerializer,
    ShoppingCartReadSerializer)
from django.shortcuts import get_object_or_404
from .permissions import IsAuthorOrReadOnlyPermission
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.response import Response
from .renderer import PlainTextRenderer
from .pagination import CustomPagination
from .filters import CustomFilter
from rest_framework.permissions import IsAuthenticated


class RecipyViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с рецептами.
    Основные методы обеспечивают CRUD-операции,
    методы favorite и shopping_cart отвечают за добавление и удаление
    рецептов в список избранного и в список покупок.
    """
    permission_classes = (IsAuthorOrReadOnlyPermission, )
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['author',]
    filter_class = CustomFilter

    def get_queryset(self):
        """
        Фильтрация по non-model fields, получение основного
        кверисета рецептов.
        """
        queryset = Recipy.objects
        if self.request.query_params.get('is_favorited'):
            recipys = [
                x.recipy.id for x in Favorite.objects.all()
                if x.user == self.request.user
            ]
            queryset = queryset.filter(id__in=recipys)

        if self.request.query_params.get('is_in_shopping_cart'):
            recipys = [
                x.recipy.id for x in ShoppingCart.objects.all()
                if x.user == self.request.user
            ]
            queryset = queryset.filter(id__in=recipys)

        tags = self.request.query_params.get('tags')
        if tags:
            print(Recipy.objects.get(id=55).tags.all())
            queryset.filter(tags__slug__in=tags.split(','))
            print('AAAAAa', tags.split(','))

        #     for tag in tags:
        #         recipy_ids = [
        #             x.id for x in Recipy.objects.all()
        #             if tags in x.tags.all()
        #         ]
        #         queryset = queryset.filter(id__in=recipy_ids)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipyReadSerializer
        return RecipyWriteSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=(IsAuthenticated, ),
        serializer_class= RecipyReadMinimalSerializer)
    def favorite(self, *args, **kwargs):
        """
        URL /recipes/<id>/favorite
        Добавить рецепт в избранное, удалить из избранного.
        """
        recipy = get_object_or_404(Recipy, id=self.kwargs.get('pk'))
        if self.request.method == 'POST':
            new_favorite = Favorite(
                user=self.request.user,
                recipy=recipy
            )
            new_favorite.save()
            serializer = self.serializer_class(recipy)
            return Response(serializer.data)

        elif self.request.method == 'DELETE':
            favorite_item = get_object_or_404(
                Favorite,
                user=self.request.user,
                recipy=recipy
            )
            favorite_item.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated, ))
    def shopping_cart(self, *args, **kwargs):
        """
        URL /recipes/<id>/shopping_cart
        Добавить рецепт в список покупок, удалить из списка покупок.
        """
        recipy = get_object_or_404(Recipy, id=self.kwargs.get('pk'))
        if self.request.method == 'POST':
            serializer = ShoppingCartReadSerializer(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                user=self.request.user,
                recipy=recipy
            )
            return Response(serializer.data)

        elif self.request.method == 'DELETE':
            shopping_cart_item = get_object_or_404(
                ShoppingCart,
                user=self.request.user,
                recipy=recipy
            )
            shopping_cart_item.delete()
            return Response(status=HTTPStatus.NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с тегами.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с ингредиентами.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
    Скачивание списка покупок.
    """
    serializer_class = ShoppingCartItemSerializer
    permission_classes = (IsAuthenticated, )
    queryset = ShoppingCart.objects.all()

    @action(
        methods=['get'],
        detail=True,
        renderer_classes=(PlainTextRenderer,))
    def download(self, *args, **kwargs):
        user = self.request.user
        current_cart = ShoppingCart.objects.filter(user=user)
        for obj in current_cart:
            ingredients = IngredientsToRecipe.objects.filter(
                recipy=obj.recipy
            ).all()
            for item in ingredients:
                ingredient = Ingredient.objects.get(id=item.ingredient.id)
                cart_item = ShoppingCartItem.objects.get_or_create(
                    cart=obj,
                    ingredient=ingredient
                )[0]
                cart_item.amount += item.amount
                cart_item.save()
        result = []
        for item in ShoppingCartItem.objects.filter(cart__in=current_cart):
            str = (
                f'{item.ingredient.name}'
                f': {item.amount} {item.ingredient.measurement_unit};\n'
            )
            result.append(str)
        cart_item.delete()

        filename = 'shopping_list.txt'
        response = HttpResponse(
            result, content_type='text/plain; charset=UTF-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(filename)
        )
        return response
