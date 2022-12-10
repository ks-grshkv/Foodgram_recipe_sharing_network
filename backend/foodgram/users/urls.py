from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (SubscriptionView, UserDeleteTokenView, UserGetTokenView,
                    UserViewSet)

router = SimpleRouter()
router.register(
    'subscriptions',
    SubscriptionView,
    basename='subscriptions',
)
router.register(
    'users',
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
    path('api/', include(router.urls)),
]
