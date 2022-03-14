from django.contrib import admin

from .models import User
from .models import (
    Tag,
    Ingredient,
    IngredientRecipe,
    Recipe,
    Favorite,
    ShoppingCart,
    Follow,
)


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email")
    list_filter = (
        "email",
        "username",
    )


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
    )
    list_filter = (
        "name",
        "tags",
        "author",
    )
    fields = (
        "author",
        "name",
        "image",
        "text",
        "tags",
        "cooking_time",
        "favorite_count",
    )
    readonly_fields = ("favorite_count",)

    def favorite_count(self, obj):
        return Favorite.objects.count()


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ("name",)


admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(IngredientRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(Follow)
