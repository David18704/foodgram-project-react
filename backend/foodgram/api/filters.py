import django_filters


from recipe.models import Recipe, User


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.ModelMultipleChoiceFilter(
        field_name="author",
        queryset=User.objects.all(),
    )
    tags__slug = django_filters.AllValuesMultipleFilter(
        field_name="tags__slug",
    )
    shopping_cart = django_filters.BooleanFilter(
        field_name="shopping_cart", lookup_expr="isnull"
    )
    favorite = django_filters.BooleanFilter(field_name="favorite", lookup_expr="isnull")

    class Meta:
        model = Recipe
        fields = (
            "author",
            "tags__slug",
            "favorite",
            "shopping_cart",
        )
