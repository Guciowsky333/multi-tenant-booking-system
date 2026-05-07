# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import CustomUserManager
from accounts.utilis import generate_verification_code


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class VerificationCode(models.Model):
    code = models.CharField(max_length=6, unique=True, default=generate_verification_code)
    email = models.EmailField(unique=True)
