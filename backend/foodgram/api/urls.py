from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import SimpleRouter

from .views import RecipyViewSet, TagViewSet, IngredientViewSet

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

urlpatterns = [
    path('/', include(router.urls)),
    # path('api-token-auth/', views.obtain_auth_token),
]
