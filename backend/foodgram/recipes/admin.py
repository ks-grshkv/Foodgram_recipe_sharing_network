from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientsToRecipe, Recipy,
                     ShoppingCart, Tag)


class IngredientsToRecipeInline(admin.TabularInline):
    model = Recipy.ingredients.through


class RecipyAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'text',
        'image',
        'cooking_time',
        'favorited_count'
    )
    inlines = [IngredientsToRecipeInline]
    readonly_fields = ('favorited_count', )
    search_fields = ('name', )
    list_filter = ('tags', 'author', 'name')
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit')
    search_fields = ('name', )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug', 'color')


admin.site.register(Recipy, RecipyAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientsToRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
