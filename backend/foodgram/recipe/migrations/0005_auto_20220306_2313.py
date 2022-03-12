# Generated by Django 2.2.16 on 2022-03-06 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipe", "0004_ingredient_amount"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="shoppingcart",
            name="unique_shopping_list",
        ),
        migrations.AddConstraint(
            model_name="follow",
            constraint=models.UniqueConstraint(
                fields=("user", "author"), name="unique_follow"
            ),
        ),
        migrations.AddConstraint(
            model_name="shoppingcart",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_shopping_cart"
            ),
        ),
    ]
