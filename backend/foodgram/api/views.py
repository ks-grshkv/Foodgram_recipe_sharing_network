from recipes.models import Recipy, Tag, Ingredient, ShoppingCart, Favorite
from rest_framework import viewsets
from users.models import User

from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import RecipySerializer, TagSerializer, IngredientSerializer, FavoriteSerializer, ShoppingCartSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from .mixins import ListCreateDestroyViewset
from rest_framework.response import Response


class RecipyViewSet(viewsets.ModelViewSet):
    queryset = Recipy.objects.all()
    serializer_class = RecipySerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('author', 'tags',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',)
    def favorite(self, *args, **kwargs):
        print('aaaaaasdsdsdasdasdad')
        print(self.kwargs)
        recipy = get_object_or_404(Recipy, id=self.kwargs.get('pk'))
        print('BBBBBBBB1')
        serializer = FavoriteSerializer(data=self.request.data)

        # print('BBBBBBBB2')
        serializer.is_valid(raise_exception=True)
        # print('BBBBBBBB3')
        serializer.save(
            user=self.request.user,
            recipy=recipy
        )
        # favorite = Favorite(user=self.request.user, recipy=recipy)
        # favorite.save()
        return Response(serializer.data)


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


# class FavoriteViewSet(viewsets.ModelViewSet):
#     # queryset = Favorite.objects.all()
#     serializer_class = FavoriteSerializer
#     # permission_classes = (IsAdminOrReadOnlyPermission,)
#     # lookup_field = 'slug'
#     pagination_class = PageNumberPagination
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('user',)
    
#     def get_queryset(self):
#         user = get_object_or_404(User, username=self.request.user.username)
#         return user.favorite.all()
    
#     def perform_create(self, serializer):
#         print('AAAAAAAA')
#         recipy = get_object_or_404(Recipy, id=self.kwargs.get('recipy_id'))
#         print('BBBBBBBB1')
#         serializer = self.serializer_class(user=self.request.user, recipy=recipy)
#         print('BBBBBBBB2')
#         serializer.is_valid(raise_exception=True)
#         print('BBBBBBBB3')
#         serializer.save()
    