import uuid

from django.db import models

from accounts.models import CustomUser
from available_rules.models import RestaurantTable
from restaurants.models import Restaurant


# Create your models here.
class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="bookings")
    table = models.ForeignKey(RestaurantTable, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(choices=Status.choices, max_length=10, default=Status.PENDING)
    date = models.DateField()
    start_time = models.TimeField()
    # Fild "end_time" will be automatically filled in during save method
    end_time = models.TimeField(null=True, blank=True)
    # token that will be snet to user to changed status from "pending" to "confirmed"
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        from datetime import datetime, timedelta

        start = datetime.combine(self.date, self.start_time)
        end = start + timedelta(minutes=self.restaurant.reservation_duration_minutes)
        self.end_time = end.time()
        super().save(*args, **kwargs)
