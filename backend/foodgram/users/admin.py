from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
        'role',)
    search_fields = ('first_name', 'last_name', 'email')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
