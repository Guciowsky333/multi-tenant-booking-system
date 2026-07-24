from django.contrib import admin

from restaurants.models import CuisineType, Restaurant, RestaurantBan


# Register your models here.
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "full_address", "cuisine_type", "created_at"]
    list_filter = ["cuisine_type", "created_at"]
    date_hierarchy = "created_at"


@admin.register(CuisineType)
class CuisineTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "id"]


@admin.register(RestaurantBan)
class RestaurantBanAdmin(admin.ModelAdmin):
    list_display = ["id", "restaurant", "get_restaurant_name", "user", "get_user_email", "created_at"]

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    def get_user_email(self, obj):
        return obj.user.email
