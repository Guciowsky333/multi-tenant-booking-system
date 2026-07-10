# Create your models here.
from django.core.validators import MinValueValidator
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

    class Meta:
        """
        Each restaurant can have only one rule per day of week.
        """

        constraints = [models.UniqueConstraint(fields=["restaurant", "day_of_week"], name="unique_day_of_week")]


class RestaurantBreak(models.Model):
    """
    In this time booking reservation on the restaurant will not be possible
    """

    class Days(models.IntegerChoices):
        MONDAY = 1, "Monday"
        TUESDAY = 2, "Tuesday"
        WEDNESDAY = 3, "Wednesday"
        THURSDAY = 4, "Thursday"
        FRIDAY = 5, "Friday"
        SATURDAY = 6, "Saturday"
        SUNDAY = 7, "Sunday"

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="restaurant_breaks")
    day_of_week = models.IntegerField(choices=Days.choices)
    start = models.TimeField()
    end = models.TimeField()


class RestaurantTable(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="restaurant_tables")
    table_number = models.CharField(max_length=10)
    seats = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    class Meta:
        """
        table_number must be unique within a restaurant
        """

        constraints = [
            models.UniqueConstraint(fields=["restaurant", "table_number"], name="unique_table_number_per_restaurant")
        ]


class RestaurantException(models.Model):
    """
    This model represent Special Rules that happen in restaurant for example when
    is some holiday or restaurant has vacation
    """

    class Type(models.TextChoices):
        CLOSED = "closed", "Closed"
        SPECIAL_HOURS = "special_hours", "Special_Hours"

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    date = models.DateField()
    type = models.CharField(max_length=13, choices=Type.choices)

    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
