from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
