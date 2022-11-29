from recipes.models import Recipy, Tag, Ingredient, ShoppingCart, Favorite
from rest_framework import viewsets

from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import RecipySerializer, TagSerializer, IngredientSerializer, FavoriteSerializer, ShoppingCartSerializer
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from .mixins import ListCreateDestroyViewset


class RecipyViewSet(viewsets.ModelViewSet):
    queryset = Recipy.objects.all()
    serializer_class = RecipySerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('author',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


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


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    # permission_classes = (IsAdminOrReadOnlyPermission,)
    # lookup_field = 'slug'
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('user',)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    # permission_classes = (IsAdminOrReadOnlyPermission,)
    # lookup_field = 'slug'
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('user',)