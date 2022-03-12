from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        _("email address"),
        max_length=254,
        unique=True,
    )
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["email", "username"], name="unique_email_username"
            )
        ]

        ordering = ["pk"]
