from django.contrib import admin
from .models import Recipy, Tag, Ingredient

admin.site.register(Recipy)
admin.site.register(Tag)
admin.site.register(Ingredient)
