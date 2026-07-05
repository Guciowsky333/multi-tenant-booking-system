from django.utils import timezone
from rest_framework import serializers

from available_rules.models import AvailableRule, RestaurantBreak, RestaurantException, RestaurantTable
from available_rules.services import validate_break


class AvailableRuleSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.SerializerMethodField()

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    class Meta:
        model = AvailableRule
        fields = ["id", "restaurant", "restaurant_name", "day_of_week", "opening_time", "closing_time"]
        read_only_fields = ["id", "restaurant_name"]
        extra_kwargs = {
            "day_of_week": {
                "help_text": "Must be unique per restaurant. Allowed values: 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday, 6=Saturday, 7=Sunday."
            }
        }

    def validate(self, data):
        if self.instance:
            """
            If an instance already exists and the user does not provide
            opening_time or closing_time (e.g. in a PATCH request),
            the missing values are taken from the existing instance
            so validation can be performed on the final state of the object.
            """
            opening_time = data.get("opening_time")
            closing_time = data.get("closing_time")
            if opening_time is None:
                opening_time = self.instance.opening_time
            if closing_time is None:
                closing_time = self.instance.closing_time

        else:
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
        fields = ["id", "restaurant", "restaurant_name", "table_number", "seats"]
        read_only_fields = ["id", "restaurant_name"]
        extra_kwargs = {"table_number": {"help_text": "This filed must be unique per restaurant"}}


class RestaurantBreakSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.SerializerMethodField()

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    class Meta:
        model = RestaurantBreak
        fields = ["id", "restaurant", "restaurant_name", "start", "end", "day_of_week"]
        read_only_fields = ["id", "restaurant_name"]

    def validate(self, data):
        if self.instance:
            """
            If an instance already exists and the user does not provide
            start or end (e.g. in a PATCH request),
            the missing values are taken from the existing instance
            so validation can be performed on the final state of the object.
            """
            start = data["start"] if "start" in data else self.instance.start
            end = data["end"] if "end" in data else self.instance.end
            restaurant = data["restaurant"] if "restaurant" in data else self.instance.restaurant
            day_of_week = data["day_of_week"] if "day_of_week" in data else self.instance.day_of_week

        else:
            start = data.get("start")
            end = data.get("end")
            restaurant = data.get("restaurant")
            day_of_week = data.get("day_of_week")

        if start and end:
            if end <= start:
                raise serializers.ValidationError("Start time must be before end time")

        # validation from services
        try:
            validate_break(
                restaurant=restaurant.id, day_of_week=day_of_week, start=start, end=end, instance=self.instance
            )
        except ValueError as e:
            raise serializers.ValidationError(str(e))

        return data


class RestaurantExceptionSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.SerializerMethodField()

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    class Meta:
        model = RestaurantException
        fields = ["id", "restaurant", "restaurant_name", "date", "type", "opening_time", "closing_time"]
        ready_only_fields = ["id", "restaurant_name"]
        extra_kwargs = {
            "opening_time": {"help_text": "Required when type is SPECIAL_HOURS. Must be empty when type is CLOSED."},
            "closing_time": {"help_text": "Required when type is SPECIAL_HOURS. Must be empty when type is CLOSED."},
        }

    def validate_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Date cannot be in the past")
        return value

    def validate(self, data):
        """
        In PATCH requests, fields not included in the request body are taken from the existing
        instance to ensure validation always runs against the final state of the object.

        Special case: if 'type' is being changed, opening_time and closing_time are NOT
        taken from the instance — the user must explicitly provide them (or leave them empty
        for CLOSED type). This prevents stale hours from a previous type from leaking into
        the new one.
        """
        if self.instance:
            type = data["type"] if "type" in data else self.instance.type

            # Flag to check if type has been changed or not
            type_changed = "type" in data and data["type"] != self.instance.type

            if type_changed:
                opening_time = data.get("opening_time")
                closing_time = data.get("closing_time")
            else:
                opening_time = data["opening_time"] if "opening_time" in data else self.instance.opening_time
                closing_time = data["closing_time"] if "closing_time" in data else self.instance.closing_time
        else:
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

            # Sets opening_time and closing_time to None if someone changed type from "SPECIAL_HOURS" to "CLOSED"
            data["opening_time"] = None
            data["closing_time"] = None

        return data
