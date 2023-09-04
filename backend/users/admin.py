from django.contrib import admin
from users.models import Subscribe, User


class SubscribeAdmin(admin.ModelAdmin):
    """Управление пользователями через админку."""
    search_fields = (
        "user__username__icontains",
        "author__username__icontains",
        "user__email__icontains",
        "author__email__icontains",
    )
    list_display = (
        "user",
        "author",
    )


class UserAdmin(admin.ModelAdmin):
    """Управление пользователями через админку."""

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "role",
    )
    list_editable = (
        "first_name",
        "last_name",
    )
    empty_value_display = "-пусто-"


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
