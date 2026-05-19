from django.contrib import admin

from restaurants.models import CuisineType, Restaurant


# Register your models here.
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ["name", "full_address", "cuisine_type", "created_at"]
    list_filter = ["cuisine_type", "created_at"]
    date_hierarchy = "created_at"


@admin.register(CuisineType)
class CuisineTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "id"]
