from django.contrib import admin
from django.utils.safestring import mark_safe
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from recipes.models import (
    Favorite,
    Ingredient,
    Recipes,
    ShoppingCart,
    Tag,
    AmountIngredient,
)


class IngredientsInline(admin.TabularInline):
    model = Ingredient


class TagsInline(admin.TabularInline):
    model = Tag


class TagAdmin(admin.ModelAdmin):
    """Управление Тегами через админку."""

    list_display = ("name", "color", "slug")
    list_filter = ("name", "color", "slug")
    search_fields = ("name", "color", "slug")


class IngredientResource(resources.ModelResource):
    """Управление Ингридиентами через админку."""

    class Meta:
        model = Ingredient


class IngredientAdmin(ImportExportModelAdmin):
    """Загрузка Ингридиентов из файла через админку."""

    resource_class = IngredientResource
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)


class IngredientInlineAdmin(admin.TabularInline):
    model = AmountIngredient


class RecipesAdmin(admin.ModelAdmin):
    """Управление Рецептами через админку."""

    search_fields = (
        "author__username__icontains",
        "author__email__icontains",
    )
    list_display = (
        "name",
        "author",
        "cooking_time",
        "preview",
    )
    list_filter = (
        "tags",
    )

    readonly_fields = ("preview",)

    def preview(self, obj):
        return mark_safe(
            f'<img src="{obj.image.url}" style="max-height: 200px;">'
        )

    preview.short_description = "Превью"
    inlines = [
        IngredientInlineAdmin,
    ]


class FavoriteAdmin(admin.ModelAdmin):
    """Управление Избранным через админку."""

    list_display = (
        "user",
        "name",
        "tags",
        "get_recipe_count",
    )
    list_filter = ("recipe__tags",)
    search_fields = (
        "user__username__icontains",
        "user__email__icontains",
        "recipe__name__icontains"
    )
    ordering = ("user",)

    def get_recipe_count(self, obj):
        return Favorite.objects.filter(
            user=obj.user,
            recipe=obj.recipe
        ).count()

    def name(self, obj):
        return obj.recipe.name

    def tags(self, obj):
        return ", ".join(tag.name for tag in obj.recipe.tags.all())

    name.short_description = "Название рецепта"
    tags.short_description = "Тэги"
    get_recipe_count.short_description = "Количество рецептов в избранном"


class ShoppingCartAdmin(admin.ModelAdmin):
    """Управление Корзиной через админку."""

    list_display = (
        "user",
        "recipe",
    )
    list_filter = ("recipe__tags",)
    search_fields = (
        "recipe__name__icontains",
        "recipe__author__username__icontains",
        "recipe__author__email__icontains",
    )
    ordering = ("user",)


class AmountIngredientAdmin(admin.ModelAdmin):
    """Управление количеством через админку."""

    list_display = ("recipe", "ingredient", "amount")
    list_filter = ("recipe__tags",)
    search_fields = (
        "recipe__name__icontains",
        "recipe__author__username__icontains",
        "recipe__author__email__icontains",
    )
    ordering = ("recipe",)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(AmountIngredient, AmountIngredientAdmin)
