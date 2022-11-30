from django.contrib import admin
from .models import Recipy, Tag, Ingredient, IngredientsToRecipe, Favorite, ShoppingCart

admin.site.register(Recipy)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(IngredientsToRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
