# Register your models here.
from django.contrib import admin

from user_reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "get_restaurant_name",
        "get_user_email",
        "rating",
        "created_at",
    ]

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    def get_user_email(self, obj):
        return obj.user.email

    get_restaurant_name.short_description = "Restaurant Name"
    get_user_email.short_description = "User Email"
