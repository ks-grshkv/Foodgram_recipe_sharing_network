from django.http import FileResponse
from recipes.models import Recipy, Tag, Ingredient, ShoppingCart, Favorite
from rest_framework import viewsets
from http import HTTPStatus
from users.models import User

from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import RecipySerializer, TagSerializer, IngredientSerializer, FavoriteSerializer, ShoppingCartSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets, renderers
from rest_framework.pagination import PageNumberPagination
from .mixins import ListCreateDestroyViewset
from rest_framework.response import Response


class RecipyViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с рецептами.
    Основные методы обеспечивают CRUD-операции,
    методы favorite и shopping_cart отвечают за добавление и удаление
    рецептов в список избранного и в список покупок.
    """
    queryset = Recipy.objects.all()
    serializer_class = RecipySerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('author', 'tags',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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
            serializer = ShoppingCartSerializer(data=self.request.data)
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
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes = (IsAdminOrReadOnlyPermission,)
    # lookup_field = 'slug'
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class PassthroughRenderer(renderers.BaseRenderer):
    """
    Return data as-is. View should supply a Response.
    """
    media_type = ''
    format = ''
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    # permission_classes = (IsAdminOrReadOnlyPermission,)
    # lookup_field = 'slug'
    # pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('user',)

    def get_queryset(self):
        cart = get_object_or_404(ShoppingCart, user_id=self.request.user.id)
        return cart

    @action(methods=['get'], detail=True, renderer_classes=(PassthroughRenderer,))
    def download(self, *args, **kwargs):
        instance = self.get_object()

        # get an open file handle (I'm just using a file attached to the model for this example):
        file_handle = instance.file.open()

        # send file
        response = FileResponse(file_handle, content_type='whatever')
        response['Content-Length'] = instance.file.size
        response['Content-Disposition'] = 'attachment; filename="%s"' % instance.file.name

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
        #параша#
    