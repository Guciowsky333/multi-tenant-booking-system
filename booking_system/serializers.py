from rest_framework import serializers

from booking_system.models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "restaurant",
            "table",
            "user",
            "status",
            "date",
            "start_time",
            "created_at",
        ]


class BookingDetailsSerializer(serializers.ModelSerializer):
    table_number = serializers.SerializerMethodField()
    table_seats = serializers.SerializerMethodField()
    restaurant_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()

    def get_table_number(self, obj):
        return obj.table.table_number

    def get_table_seats(self, obj):
        return obj.table.seats

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    def get_user_email(self, obj):
        return obj.user.email

    class Meta:
        model = Booking
        fields = [
            "id",
            "restaurant",
            "restaurant_name",
            "table",
            "table_number",
            "table_seats",
            "user_email",
            "status",
            "date",
            "start_time",
            "created_at",
        ]
        read_only_fields = ["restaurant_name", "table_number", "table_seats", "user_email", "created_at"]
