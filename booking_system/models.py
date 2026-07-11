import uuid

from django.db import models

from accounts.models import CustomUser
from available_rules.models import RestaurantTable
from restaurants.models import Restaurant


# Create your models here.
class Booking(models.Model):
    class Role(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="bookings")
    table = models.ForeignKey(RestaurantTable, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(choices=Role.choices, max_length=10)
    date = models.DateTimeField(auto_now_add=True)
    start_time = models.TimeField()
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
