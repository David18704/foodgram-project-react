from django.urls import path, include
from rest_framework import routers
from .views import TagViewSet, IngredientViewSet, RecipeViewSet, UserViewSet


router = routers.DefaultRouter()

router.register(r"users", UserViewSet, basename="users")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")


urlpatterns = [
    path("api", include(router.urls)),
]
