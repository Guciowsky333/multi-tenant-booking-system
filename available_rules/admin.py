# Register your models here.
from django.contrib import admin

from available_rules.models import AvailableRule, RestaurantBreak, RestaurantException, RestaurantTable


@admin.register(AvailableRule)
class AvailableRuleAdmin(admin.ModelAdmin):
    list_display = ["restaurant__name", "day_of_week", "opening_time", "closing_time"]


@admin.register(RestaurantTable)
class RestaurantTableAdmin(admin.ModelAdmin):
    list_display = ["restaurant__name", "table_number", "seats"]


@admin.register(RestaurantBreak)
class RestaurantBreakAdmin(admin.ModelAdmin):
    list_display = ["restaurant__name", "start", "end"]


@admin.register(RestaurantException)
class RestaurantExceptionAdmin(admin.ModelAdmin):
    list_display = ["restaurant__name", "date", "type"]
