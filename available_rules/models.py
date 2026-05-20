# Create your models here.
from django.db import models

from restaurants.models import Restaurant


class AvailableRule(models.Model):
    class Days(models.IntegerChoices):
        MONDAY = 1, "Monday"
        TUESDAY = 2, "Tuesday"
        WEDNESDAY = 3, "Wednesday"
        THURSDAY = 4, "Thursday"
        FRIDAY = 5, "Friday"
        SATURDAY = 6, "Saturday"
        SUNDAY = 7, "Sunday"

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="available_rules")
    day_of_week = models.IntegerField(choices=Days.choices)
    opening_time = models.TimeField()
    closing_time = models.TimeField()


class RestaurantTable(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    table_number = models.CharField(max_length=10)
    seats = models.PositiveIntegerField()

    class Meta:
        """
        table_number must be unique within a restaurant
        """

        constraints = [
            models.UniqueConstraint(fields=["restaurant", "table_number"], name="unique_table_number_per_restaurant")
        ]


class RestaurantBreak(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    start = models.TimeField()
    end = models.TimeField()


class RestaurantException(models.Model):
    """
    This model represent Special Rules that happen in restaurant for example when
    is some holiday or restaurant has vacation
    """

    class Type(models.IntegerChoices):
        CLOSED = "closed", "Closed"
        SPECIAL_HOURS = "special Hours", "Special Hours"

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    date = models.DateField()
    type = models.IntegerField(choices=Type.choices)

    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
