from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from accounts.models import CustomUser
from restaurants.models import Restaurant

# Create your models here.


class Review(models.Model):
    comment = models.TextField(max_length=300, null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="reviews")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        User can add only one review per restaurant.
        """

        constraints = [models.UniqueConstraint(fields=["user", "restaurant"], name="unique_user_review")]
