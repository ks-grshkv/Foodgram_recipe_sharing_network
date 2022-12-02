from django.urls import include, path

from .views import UserGetTokenView, UserViewSet, UserDeleteTokenView
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(
    'users',
    UserViewSet,
    basename='users',
)
# router.register(
#     'subscriptions',
#     SubscriptionViewSet,
#     basename='subscriptions',
# )
# router.register(
#     'users/(?P<author_id>\\d+)/subscribe',
#     SubscriptionViewSet,
#     basename='subscriptions'
# )

urlpatterns = [
    # path('users/subscriptions/', SubscriptionViewSet.as_view({'delete': 'destroy', 'post': 'create'}), name='subscribe'),
    # path('users/', UserRegisterView.as_view(), name='signup'),
    path('auth/token/login/', UserGetTokenView.as_view(), name='login'),
    path('auth/token/logout/', UserDeleteTokenView.as_view(), name='login'),
    path('', include(router.urls)),
]
