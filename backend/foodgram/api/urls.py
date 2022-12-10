from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet)

app_name = 'api'

router = SimpleRouter()
router.register(
    'recipes',
    RecipeViewSet,
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

urlpatterns = [
    path('', include(router.urls)),
]
