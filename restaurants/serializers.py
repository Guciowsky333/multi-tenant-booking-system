from rest_framework import serializers

from restaurants.models import CuisineType, Restaurant


class CuisineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuisineType
        fields = ["id", "name"]


class RestaurantSerializer(serializers.ModelSerializer):
    full_address = serializers.SerializerMethodField()
    average_review_rating = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)

    # Propery method in model restaurant
    def get_full_address(self, obj):
        return obj.full_address

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
            "reservation_duration_minutes",
            "full_address",
            "average_review_rating",
        ]
        read_only_fields = ["full_address", "average_review_rating"]
