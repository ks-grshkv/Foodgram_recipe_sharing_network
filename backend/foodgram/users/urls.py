from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (SubscriptionView, UserDeleteTokenView, UserGetTokenView,
                    UserViewSet)

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
