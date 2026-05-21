from rest_framework import serializers

from available_rules.models import AvailableRule


class AvailableRuleSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.SerializerMethodField()

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    class Meta:
        model = AvailableRule
        fields = ["restaurant", "restaurant_name", "day_of_week", "opening_time", "closing_time"]
        read_only_fields = ["restaurant_name"]
