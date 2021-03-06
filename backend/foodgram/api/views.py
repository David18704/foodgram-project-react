import io

from django.db.models import Exists, OuterRef
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Count
from rest_framework import status, viewsets, filters
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from collections import Counter

from .serializers import (
    TagSerializer,
    UserSerializer,
    UserRegistrationSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipeCreateSerializer,
    MyAuthTokenSerializer,
    PasswordSerializer,
    RecipeFavoriteSerializer,
    FollowUserSerializer,
    ShoppingCartSerializer,
)
from .filters import RecipeFilter
from .pagination import FoodgrampPagination
from recipe.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart, Follow

User = get_user_model()


class Logout(APIView):
    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = MyAuthTokenSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = User.objects.annotate(
            is_subscribed=Exists(
                Follow.objects.filter(author=self.request.user, user__pk=OuterRef("pk"))
            )
        )
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve" or self.action == "list":
            return UserSerializer
        return UserRegistrationSerializer

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
        url_path="me",
    )
    def current_user(self, request):
        serializer = self.get_serializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[
            IsAuthenticated,
        ],
        url_path="subscribe",
    )
    def subscribe(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        user = request.user
        if request.method == "POST":
            if Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    {"errors": "???????????????? ?????????????????? ???????????????? ??????????????????"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if request.user != author:
                Follow.objects.create(user=request.user, author=author)
                data = UserSerializer(author, context={"request": request}).data
                return Response(data, status=status.HTTP_201_CREATED)
            return Response({"errors": "????????????"}, status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk):
        author = get_object_or_404(User, pk=pk)
        user = request.user
        if Follow.objects.filter(user=user, author=author).exists() is False:
            return Response(
                {"errors": "???????????? ???? ????????????"}, status=status.HTTP_404_NOT_FOUND
            )
        Follow.objects.filter(user=user, author=author).delete()
        return Response("???????????????? ??????????????", status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[
            IsAuthenticated,
        ],
        url_path="subscriptions",
    )
    def subscriptions(self, request):
        user = request.user
        user = get_object_or_404(User, username=user.username)
        subscriptions = Follow.objects.filter(user=request.user)
        annotateed_subscriptions = subscriptions.annotate(
            recipes_count=Count("author__recipes"),
            is_subscribed=Count("author__follower"),
        )
        data = FollowUserSerializer(annotateed_subscriptions, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[
            IsAuthenticated,
        ],
        url_path="set_password",
    )
    def set_password(self, request):
        user = request.user
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response("???????????? ?????????????? ??????????????", status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):

    pagination_class = FoodgrampPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ("author", "tags__slug", "favorite", "shopping_cart")
    filterset_class = RecipeFilter
    ordering_fields = "pk"

    def get_queryset(self):
        queryset = Recipe.objects.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    user=self.request.user, recipe__pk=OuterRef("pk")
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    user=self.request.user, recipe__pk=OuterRef("pk")
                )
            ),
        )
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve" or self.action == "list":
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[
            IsAuthenticated,
        ],
        url_path="shopping_cart",
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == "POST":
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"errors": "???????????? ?????? ???????????????? ?? ???????????? ??????????????"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            data = RecipeFavoriteSerializer(recipe, context={"request": request}).data
            return Response(data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists() is False:
                return Response(
                    {"errors": "???????????? ???? ????????????"}, status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
            return Response(
                "???????????? ?????????????? ???????????? ???? ???????????? ??????????????",
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[
            IsAuthenticated,
        ],
        url_path="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
        subscriptions = ShoppingCart.objects.filter(user=request.user)
        data = ShoppingCartSerializer(subscriptions, many=True).data
        shopping_cart = io.BytesIO()
        pdfmetrics.registerFont(TTFont("DejaVuSerif", "DejaVuSerif.ttf", "UTF-8"))
        p = canvas.Canvas(shopping_cart)
        p.setFont("DejaVuSerif", 16)
        count = Counter()
        for cart in data:
            for recipe in cart["ingredients"]:
                count[recipe["name"], recipe["measurement_unit"]] += recipe["amount"]
                b = dict(count)
                keys = list(b.keys())
                values = list(b.values())
        for f in range(len(keys)):
            p.drawString(150, 800 - f * 50, str(keys[f]) + "  " + str(values[f]))
        p.showPage()
        p.save()
        shopping_cart.seek(0)
        return FileResponse(
            shopping_cart, as_attachment=True, filename="recipe_shopping_cart.pdf"
        )

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[
            IsAuthenticated,
        ],
        url_path="favorite",
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == "POST":
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"errors": "????????????  ???????????????????? ?? ??????????????????"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Favorite.objects.create(user=user, recipe=recipe)
            data = RecipeFavoriteSerializer(recipe, context={"request": request}).data
            return Response(data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if Favorite.objects.filter(user=user, recipe=recipe).exists() is False:
                return Response(
                    {"errors": "????????????  ???????????????? ???? ????????????????????"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response("???????????? ?????????????? ????????????", status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    http_method_names = ["get"]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)
