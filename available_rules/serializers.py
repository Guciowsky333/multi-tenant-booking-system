from django.utils import timezone
from rest_framework import serializers

from available_rules.models import AvailableRule, RestaurantBreak, RestaurantException, RestaurantTable


class AvailableRuleSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.SerializerMethodField()

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    class Meta:
        model = AvailableRule
        fields = ["restaurant", "restaurant_name", "day_of_week", "opening_time", "closing_time"]
        read_only_fields = ["restaurant_name"]
        extra_kwargs = {
            "day_of_week": {
                "help_text": "Must be unique per restaurant. Allowed values: 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday, 7=Sunday."
            }
        }

    def validate(self, data):
        opening_time = data.get("opening_time")
        closing_time = data.get("closing_time")
        if opening_time and closing_time:
            if closing_time <= opening_time:
                raise serializers.ValidationError("Closing time must be after opening time")
        return data


class RestaurantTableSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.SerializerMethodField()

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    class Meta:
        model = RestaurantTable
        fields = ["restaurant", "restaurant_name", "table_number", "seats"]
        read_only_fields = ["restaurant_name"]
        extra_kwargs = {"table_number": {"help_text": "This filed must be unique per restaurant"}}


class RestaurantBreakSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.SerializerMethodField()

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    class Meta:
        model = RestaurantBreak
        fields = ["restaurant", "restaurant_name", "start", "end"]
        read_only_fields = ["restaurant_name"]

    def validate(self, data):
        start = data.get("start")
        end = data.get("end")

        if start and end:
            if end <= start:
                raise serializers.ValidationError("Start time must be before end time")
        return data


class RestaurantExceptionSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.SerializerMethodField()

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    class Meta:
        model = RestaurantException
        fields = ["restaurant", "restaurant_name", "date", "type", "opening_time", "closing_time"]
        extra_kwargs = {
            "opening_time": {"help_text": "Required when type is SPECIAL_HOURS. Must be empty when type is CLOSED."}
        }

    def validate_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Date cannot be in the past")
        return value

    def validate(self, data):
        type = data.get("type")
        opening_time = data.get("opening_time")
        closing_time = data.get("closing_time")

        if type == RestaurantException.Type.SPECIAL_HOURS:
            if not opening_time or not closing_time:
                raise serializers.ValidationError(
                    "Opening time and closing time must be specified when type is SPECIAL_HOURS"
                )
            if closing_time <= opening_time:
                raise serializers.ValidationError("Closing time must be after opening time")

        if type == RestaurantException.Type.CLOSED:
            if opening_time or closing_time:
                raise serializers.ValidationError("Opening time and closing time must be empty when type is CLOSED")

        return data
