from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class IngredientsToRecipeInline(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'text',
        'image',
        'cooking_time',
        'favorited_count',
    )
    inlines = [IngredientsToRecipeInline]
    readonly_fields = ('favorited_count', )
    search_fields = ('name', )
    list_filter = ('tags', 'author', 'name')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit')
    search_fields = ('name', )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug', 'color')


admin.site.register(Favorite)
admin.site.register(ShoppingCart)
