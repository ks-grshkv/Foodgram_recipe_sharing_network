from http import HTTPStatus

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientsToRecipe, Recipe,
                            ShoppingCart, Tag)
from users.serializers import RecipeReadMinimalSerializer

from .filters import RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnlyPermission
from .renderer import PlainTextRenderer
from .serializers import (IngredientSerializer,
                          RecipeReadSerializer,
                          RecipeWriteSerializer,
                          TagSerializer)


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
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_serializer_context(self):
        """
        Дополнительные данные для контекста сериализатора.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'kwargs': self.kwargs
        }

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
        context = self.get_serializer_context()
        context['action'] = 'favorite'
        if self.request.method == 'POST':
            serializer = self.serializer_class(
                data=self.request.data,
                context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
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
        serializer_class=RecipeReadMinimalSerializer,
        permission_classes=(IsAuthenticated, ))
    def shopping_cart(self, *args, **kwargs):
        """
        URL /recipes/<id>/shopping_cart
        Добавить рецепт в список покупок, удалить из списка покупок.
        """
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        context = self.get_serializer_context()
        context['action'] = 'shopping_cart'

        if self.request.method == 'POST':
            serializer = self.serializer_class(
                data=self.request.data,
                context=context
            )
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

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        renderer_classes=(PlainTextRenderer, ),
        permission_classes=(IsAuthenticated, ))
    def download_shopping_cart(self, *args, **kwargs):
        """
        URL /recipes/download_shopping_cart
        Cкачать список покупок.
        """
        user = self.request.user
        current_cart = ShoppingCart.objects.filter(user=user)
        cart_dict = {}
        for obj in current_cart:
            ingredients = IngredientsToRecipe.objects.filter(
                recipe=obj.recipe
            ).all()
            for item in ingredients:
                ingredient = get_object_or_404(
                    Ingredient,
                    id=item.ingredient.id
                )
                try:
                    cart_dict[ingredient] += item.amount
                except Exception:
                    cart_dict[ingredient] = 0
                    cart_dict[ingredient] += item.amount

        result = []
        for item in cart_dict.keys():
            str = (
                f'{item} : {cart_dict[item]}\n'
            )
            result.append(str)

        filename = 'shopping_list.txt'
        response = HttpResponse(
            result, content_type='text/plain; charset=UTF-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(filename)
        )
        return response


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
    pagination_class = None
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['^name',]
