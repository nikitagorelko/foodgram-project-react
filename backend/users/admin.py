from django.contrib import admin

from users.models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'password',
        'first_name',
        'last_name',
    )
    list_editable = ('password',)
    list_filter = ('username', 'email')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
