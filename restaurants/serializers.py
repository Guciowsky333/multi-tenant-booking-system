from rest_framework import serializers

from available_rules.serializers import (
    AvailableRuleBriefSerializer,
    RestaurantBreakBriefSerializer,
    RestaurantTableBriefSerializer,
)
from menus.serializers import MenuBriefSerializer
from restaurants.models import CuisineType, Restaurant


class CuisineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuisineType
        fields = ["id", "name"]


class RestaurantSerializer(serializers.ModelSerializer):
    average_review_rating = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)

    # Propery method in model restaurant
    def get_average_review_rating(self, obj):
        return obj.average_review_rating

    class Meta:
        model = Restaurant
        fields = [
            "id",
            "name",
            "cuisine_type",
            "address",
            "city",
            "image",
            "average_review_rating",
        ]
        read_only_fields = ["average_review_rating"]


class RestaurantDetailSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    average_review_rating = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()
    menus = MenuBriefSerializer(many=True, read_only=True)
    available_rules = AvailableRuleBriefSerializer(many=True, read_only=True)
    restaurant_breaks = RestaurantBreakBriefSerializer(many=True, read_only=True)
    restaurant_tables = RestaurantTableBriefSerializer(many=True, read_only=True)

    # Propery method in model restaurant
    def get_average_review_rating(self, obj):
        return obj.average_review_rating

    # Propery method in model restaurant
    def get_full_address(self, obj):
        return obj.full_address

    class Meta:
        model = Restaurant
        fields = [
            "id",
            "name",
            "cuisine_type",
            "address",
            "city",
            "full_address",
            "image",
            "average_review_rating",
            "menus",
            "available_rules",
            "restaurant_breaks",
            "restaurant_tables",
        ]
