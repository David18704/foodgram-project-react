# Generated by Django 2.2.16 on 2022-02-11 21:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("recipe", "0002_auto_20220208_2021"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ingredient",
            name="amount",
        ),
    ]
