from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from drf_extra_fields.fields import Base64ImageField

from recipe.models import (
    Tag,
    Ingredient,
    IngredientRecipe,
    Recipe,
    Follow,
    ShoppingCart,
)

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "username", "password")


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "username", "is_subscribed")

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class MyAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label=("Email"))
    password = serializers.CharField(
        label=("Password",), style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )
            if not user:
                msg = "Unable to log in with provided credentials."
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("name", "color", "slug", "id")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "amount", "name", "measurement_unit")


class IngredientCreateSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ("id", "amount")


class RecipeGetSerializer(serializers.ModelSerializer):
    ingredients = IngredientGetSerializer(many=True, required=False)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(max_length=None)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "author",
            "name",
            "text",
            "ingredients",
            "tags",
            "cooking_time",
            "image",
            "is_favorited",
            "is_in_shopping_cart",
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientCreateSerializer(many=True, required=False)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            "author",
            "name",
            "text",
            "ingredients",
            "tags",
            "cooking_time",
            "image",
        )

    def validate(self, data):
        if data["cooking_time"] <= 0:
            raise serializers.ValidationError("Ошибка")
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            first_ingredient = get_object_or_404(Ingredient, id=ingredient["id"])
            IngredientRecipe.objects.create(
                recipe=recipe, ingredient=first_ingredient, amount=ingredient["amount"]
            )
        return recipe

    def update(self, instance, validated_data):
        if "tags" in validated_data:
            tags = validated_data.pop("tags")
            instance.tags.clear()
            for tag in tags:
                instance.tags.add(tag)
        if "ingredients" in validated_data:
            ingredients = validated_data.pop("ingredients")
            instance.ingredients.clear()
            for ingredient in ingredients:
                ingredient_id = ingredient["id"]
                amount = ingredient["amount"]
                new_ingredient = get_object_or_404(Ingredient, id=ingredient_id)
                ingredients_recipe = IngredientRecipe.objects.create(
                    recipe=instance, ingredient=new_ingredient, amount=amount
                )
                instance.ingredients.add(new_ingredient)
        return super().update(instance, validated_data)


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = ("name", "image", "cooking_time")


class ShoppingCartSerializer(serializers.ModelSerializer):
    ingredients = IngredientGetSerializer(
        source="recipe.ingredients", many=True, required=False
    )

    class Meta:
        model = ShoppingCart
        fields = ("ingredients",)


class PasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    class Meta:
        model = User
        fields = ("new_password", "current_password")
        extra_kwargs = {"current_password": {"write_only": True}}


class FollowUserSerializer(serializers.ModelSerializer):
    recipes = RecipeFavoriteSerializer(
        source="author.recipes", many=True, required=False
    )
    username = serializers.CharField(source="author.username")
    id = serializers.CharField(source="author.id")
    first_name = serializers.CharField(source="author.first_name")
    last_name = serializers.CharField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    email = serializers.CharField(source="author.email")
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        if obj.author.follower.exists():
            return True
        return False

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.CharField()
    author = serializers.CharField()

    class Meta:
        model = Follow
        fields = ("user", "author")
