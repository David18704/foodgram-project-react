from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название тэга")
    color = models.CharField(max_length=40, verbose_name="цвет тэга")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="слаг")

    def __str__(self):
        return f"{self.name}, {self.slug}"


class Ingredient(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название ингридиента")
    measurement_unit = models.CharField(max_length=64, verbose_name="единица измерения")
    amount = models.PositiveSmallIntegerField(blank=True, verbose_name="Количество")

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        related_name="recipes",
        through="IngredientRecipe",
    )
    tags = models.ManyToManyField(Tag, verbose_name="Тэги", related_name="recipes")
    author = models.ForeignKey(
        User, verbose_name="Автор", related_name="recipes", on_delete=models.CASCADE
    )
    text = models.TextField(verbose_name="Текст рецепта")
    image = models.ImageField(
        verbose_name="Картинка", upload_to="media/recipes/images/"
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления в минутах",
    )


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="ингридиент рецепта",
        related_name="ingredient_recipe",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Название рецепта",
        on_delete=models.CASCADE,
        related_name="ingredient_recipe",
    )
    amount = models.PositiveSmallIntegerField(blank=True, verbose_name="Количество")


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="shopping_cart",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Название рецепта",
        related_name="shopping_cart",
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="favorite",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Название рецепта",
        related_name="favorite",
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_list"
            )
        ]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User, verbose_name="Автор", on_delete=models.CASCADE, related_name="following"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "author"], name="unique_follow")
        ]

    def __str__(self):
        return f"{self.user}, {self.author}"
