from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (IngredientViewSet, RecipyViewSet, ShoppingCartViewSet,
                    TagViewSet)

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

urlpatterns = [
    path('/', include(router.urls)),
]
