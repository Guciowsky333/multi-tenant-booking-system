from rest_framework import serializers

from available_rules.models import AvailableRule, RestaurantTable


class AvailableRuleSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.SerializerMethodField()

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    class Meta:
        model = AvailableRule
        fields = ["restaurant", "restaurant_name", "day_of_week", "opening_time", "closing_time"]
        read_only_fields = ["restaurant_name"]

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
