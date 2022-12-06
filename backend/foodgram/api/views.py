from django.http import HttpResponse
from recipes.models import ShoppingCartItem, Recipy, Tag, Ingredient, ShoppingCart, Favorite, IngredientsToRecipe
from rest_framework import viewsets
from http import HTTPStatus
from users.models import User
import json

from .permissions import IsAuthorOrReadOnlyPermission, OwnerAdmin
from .serializers import RecipyReadSerializer, RecipyWriteSerializer, TagSerializer, IngredientSerializer, FavoriteSerializer, ShoppingCartItemSerializer, ShoppingCartReadSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets, renderers
from rest_framework.pagination import PageNumberPagination
from .mixins import ListCreateDestroyViewset
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .renderer import PlainTextRenderer
from .pagination import CustomPagination


class RecipyViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с рецептами.
    Основные методы обеспечивают CRUD-операции,
    методы favorite и shopping_cart отвечают за добавление и удаление
    рецептов в список избранного и в список покупок.
    """
    permission_classes = (OwnerAdmin, )
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['author', 'tags', ]

    def get_queryset(self):
        if self.request.query_params.get('is_favorite'):
            recipys = [x.recipy for x in Favorite.objects.all() if x.user == self.request.user]
            recipy_ids = [x.id for x in recipys]
            qs = Recipy.objects.filter(id__in=recipy_ids)
            return qs
        if self.request.query_params.get('is_in_shopping_cart'):
            recipys = [x.recipy for x in ShoppingCart.objects.all() if x.user == self.request.user]
            recipy_ids = [x.id for x in recipys]
            qs = Recipy.objects.filter(id__in=recipy_ids)
            return qs
        return Recipy.objects.all()

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipyReadSerializer
        return RecipyWriteSerializer

    # def perform_create(self, serializer):
    #     print('AAAAAA PERFORM CREATE')
    #     serializer.save()
    #     serializer = RecipyReadSerializer(data=self.request.data)
    #     print('AAAAAA VALIDATING')
    #     serializer.is_valid(raise_exception=True)
    #     print('RETURNING')
    #     return Response(RecipyWriteSerializer(data=self.request.data).data)

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, *args, **kwargs):
        """
        URL /recipes/<id>/favorite
        Добавить рецепт в избранное \ удалить из избранного.
        """
        recipy = get_object_or_404(Recipy, id=self.kwargs.get('pk'))
        if self.request.method == 'POST':
            serializer = FavoriteSerializer(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                user=self.request.user,
                recipy=recipy
            )
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        elif self.request.method == 'DELETE':
            favorite_item = get_object_or_404(
                Favorite,
                user=self.request.user,
                recipy=recipy
            )
            favorite_item.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, *args, **kwargs):
        """
        URL /recipes/<id>/shopping_cart
        Добавить рецепт в список покупок \ удалить из списка покупок.
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
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes = (IsAdminOrReadOnlyPermission,)
    # lookup_field = 'slug'
    pagination_class = None
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes = (IsAdminOrReadOnlyPermission,)
    # lookup_field = 'slug'
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartReadSerializer
    # permission_classes = (IsAdminOrReadOnlyPermission,)
    # lookup_field = 'slug'
    # pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('user',)
    queryset = ShoppingCart.objects.all()

    def get_object(self):
        cart = get_object_or_404(ShoppingCart, user_id=self.request.user.id)
        return cart

    @action(methods=['get'], detail=True, renderer_classes=(PlainTextRenderer,), serializer_class=ShoppingCartItemSerializer)
    def download(self, *args, **kwargs):
        user = self.request.user
        current_cart = ShoppingCart.objects.filter(user=user)
        for obj in current_cart:
            ingredients = IngredientsToRecipe.objects.filter(recipy=obj.recipy).all()
            for item in ingredients:
                ingredient = Ingredient.objects.get(id=item.ingredient.id)
                cart_item = ShoppingCartItem.objects.get_or_create(cart=obj, ingredient=ingredient)[0]
                cart_item.amount += item.amount
                cart_item.save()
        result = []
        for item in ShoppingCartItem.objects.filter(cart__in=current_cart):
            str = f'{item.ingredient.name}: {item.amount} {item.ingredient.measurement_unit};\n'
            result.append(str)
        cart_item.delete()

        filename = 'shopping_list.txt'
        response = HttpResponse(result, content_type='text/plain; charset=UTF-8')
        # response['Content-Disposition'] = 'attachment; filename="%s"' % instance.file
        response['Content-Disposition'] = ('attachment; filename={0}'.format(filename))
        return response


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    # permission_classes = (IsAdminOrReadOnlyPermission,)
    # lookup_field = 'slug'
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('user',)
    
    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return user.favorite.all()
        # параша
    