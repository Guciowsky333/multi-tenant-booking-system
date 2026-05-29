# Create your models here.
from django.db import models

from accounts.models import CustomUser
from restaurants.models import Restaurant


class MemberShip(models.Model):
    class Role(models.TextChoices):
        MANAGER = "manager", "Manager"
        STAFF = "staff", "Staff"

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(choices=Role.choices, max_length=7)

    class Meta:
        """
        User can only have one MemberShip model per restaurant.
        """

        constraints = [models.UniqueConstraint(fields=["user", "restaurant"], name="unique_membership")]
