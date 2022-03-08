import django_filters


from recipe.models import Recipe, User


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.ModelMultipleChoiceFilter(
        field_name='author', 
        
        queryset=User.objects.all(),
    )
    tags__slug = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug',      
    )
    shopping_cart = django_filters.BooleanFilter(field_name='shopping_cart', method='filter_shopping_cart')
    
    def filter_shopping_cart(self,queryset,name,value):     
        lookup = '__'.join([name, 'isnull'])
        return queryset.filter(**{lookup: False})

    favorite = django_filters.BooleanFilter(field_name='favorite', method='filter_is_favorited')

    def filter_is_favorited(self,queryset,name,value):
        
        lookup = '__'.join([name, 'isnull'])
        return queryset.filter(**{lookup: False})

    class Meta:
        model = Recipe
        fields = ('author', 'tags__slug', 'favorite', 'shopping_cart',)
