from django.contrib import admin

from menus.models import Dish, Menu


# Register your models here.
@admin.register(Menu)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["get_restaurant_name", "name"]

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    get_restaurant_name.short_description = "Restaurant Name"


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ["menu", "name", "price"]
