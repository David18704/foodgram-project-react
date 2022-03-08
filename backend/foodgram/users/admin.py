from django.contrib import admin

from .models import User 
from recipe.models import Tag, Ingredient, IngredientRecipe, Recipe, Favorite, ShoppingCart, Follow

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    list_filter = ('email',  'username',)

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'favorite_count',)
    list_filter = ('name', 'tags', 'author',)
    
    def favorite_count(self, obj):
        return Favorite.objects.count()
        
class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)
  
admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(IngredientRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(Follow)
