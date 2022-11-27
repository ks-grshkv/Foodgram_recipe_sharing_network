from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('recipy/<id>/', views.recipy_detail),
    path('tag/<tag>/', views.get_recipes_by_tag),

]