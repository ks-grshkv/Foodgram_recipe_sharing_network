from django.urls import include, path
from .views import (
    UserGetTokenView,
    UserViewSet,
    UserDeleteTokenView,
    SubscriptionView)
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(
    'api/users/subscriptions',
    SubscriptionView,
    basename='subscriptions',
)
router.register(
    'api/users',
    UserViewSet,
    basename='users',
)

urlpatterns = [
    path(
        'api/auth/token/login/',
        UserGetTokenView.as_view(),
        name='login'
    ),
    path(
        'api/auth/token/logout/',
        UserDeleteTokenView.as_view(),
        name='login'
    ),
    # path(
    #     'api/users/subscriptions/',
    #     SubscriptionView.as_view({'get': 'list'}),
    #     name='subscriptions'
    # ),

    path('', include(router.urls)),
]
