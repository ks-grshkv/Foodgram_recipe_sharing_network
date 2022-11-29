from django.urls import path

from .views import UserGetTokenView, UserRegisterView

urlpatterns = [
    path('users/', UserRegisterView.as_view(), name='signup'),
    path('auth/token/login/', UserGetTokenView.as_view(), name='login'),
]
