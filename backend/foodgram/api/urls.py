from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    RecipyViewSet,
    TagViewSet,
    IngredientViewSet,
    ShoppingCartViewSet,
    FavoriteViewSet)

app_name = 'api'

router = SimpleRouter()
router.register(
    'recipes',
    RecipyViewSet,
    basename='recipes',
)
router.register(
    'tags',
    TagViewSet,
    basename='tags',
)
router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients',
)
router.register(
    'cart',
    ShoppingCartViewSet,
    basename='cart',
)
router.register(
    'favorite',
    FavoriteViewSet,
    basename='favorite',
)

urlpatterns = [
    path('/', include(router.urls)),
]
