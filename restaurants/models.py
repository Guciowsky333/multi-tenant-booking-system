from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Avg

from accounts.models import CustomUser


# Create your models here.
class CuisineType(models.Model):
    """
    Represents a type of cuisine.This model will be manage only by admin
    through the admin panel.
    """

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    name = models.CharField(max_length=100, unique=True)
    cuisine_type = models.ForeignKey(CuisineType, on_delete=models.PROTECT)
    owner = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    image = models.ImageField(upload_to="restaurant_images", null=True, blank=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    reservation_duration_minutes = models.IntegerField(default=90, validators=[MinValueValidator(1)])
    reservation_interval_minutes = models.IntegerField(default=30, validators=[MinValueValidator(1)])

    @property
    def full_address(self):
        return f"{self.city.upper()}, {self.address}"

    @property
    def average_review_rating(self):
        """
        Returns the average rating of the restaurant.
        """
        average = self.reviews.aggregate(Avg("rating"))
        # If restaurant has not any reviews returns 0
        return round(average["rating__avg"], 2) if average["rating__avg"] else 0

    def __str__(self):
        return self.name
