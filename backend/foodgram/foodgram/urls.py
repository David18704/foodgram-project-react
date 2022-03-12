from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import routers

from api.views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    UserViewSet,
    Logout,
    CustomAuthToken,
)


router = routers.DefaultRouter()

router.register(r"users", UserViewSet, basename="users")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("api/", include("api.urls")),
    path("admin/", admin.site.urls),
    path("api/auth/token/login/", CustomAuthToken.as_view()),
    path("api/auth/token/logout/", Logout.as_view(), name="logout"),
    path("api/", include(router.urls)),
]
