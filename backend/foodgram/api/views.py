from http import HTTPStatus

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientsToRecipe, Recipe,
                            ShoppingCart, ShoppingCartItem, Tag)
from users.serializers import RecipeReadMinimalSerializer

from .filters import RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnlyPermission
from .renderer import PlainTextRenderer
from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, ShoppingCartItemSerializer,
                          ShoppingCartReadSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
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
    filterset_class = RecipeFilter

    def get_queryset(self):
        """
        Фильтрация по non-model fields, получение основного
        кверисета рецептов.
        """
        queryset = Recipe.objects.all()
        # if self.request.query_params.get('is_favorited'):
        #     recipes = [
        #         x.recipe.id for x in Favorite.objects.all()
        #         if x.user == self.request.user
        #     ]
        #     queryset = queryset.filter(id__in=recipes)

        # if self.request.query_params.get('is_in_shopping_cart'):
        #     recipes = [
        #         x.recipe.id for x in ShoppingCart.objects.all()
        #         if x.user == self.request.user
        #     ]
        #     queryset = queryset.filter(id__in=recipes)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=(IsAuthenticated, ),
        serializer_class=RecipeReadMinimalSerializer)
    def favorite(self, *args, **kwargs):
        """
        URL /recipes/<id>/favorite
        Добавить рецепт в избранное, удалить из избранного.
        """
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        if self.request.method == 'POST':
            new_favorite = Favorite(
                user=self.request.user,
                recipe=recipe
            )
            new_favorite.save()
            serializer = self.serializer_class(recipe)
            return Response(serializer.data)

        elif self.request.method == 'DELETE':
            favorite_item = get_object_or_404(
                Favorite,
                user=self.request.user,
                recipe=recipe
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
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        if self.request.method == 'POST':
            serializer = ShoppingCartReadSerializer(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                user=self.request.user,
                recipe=recipe
            )
            return Response(serializer.data)

        elif self.request.method == 'DELETE':
            shopping_cart_item = get_object_or_404(
                ShoppingCart,
                user=self.request.user,
                recipe=recipe
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
                recipe=obj.recipe
            ).all()
            for item in ingredients:
                ingredient = get_object_or_404(
                    Ingredient,
                    id=item.ingredient.id
                )
                cart_item = ShoppingCartItem.objects.get_or_create(
                    cart=obj,
                    ingredient=ingredient
                )[0]
                cart_item.amount += item.amount
                cart_item.save()
            # ShoppingCartItem.objects.bulk_create(cart_item_list)
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
