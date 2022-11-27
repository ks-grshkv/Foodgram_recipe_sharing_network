from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.create_user),
    path('signin/', views.sign_in),
]
