from rest_framework import serializers

from menus.models import Dish, Menu


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ["id", "menu", "name", "price", "description", "image"]


class MenuSerializer(serializers.ModelSerializer):
    dishes = DishSerializer(many=True, read_only=True)
    restaurant_name = serializers.SerializerMethodField()

    def get_restaurant_name(self, obj):
        return obj.restaurant_name

    class Meta:
        model = Menu
        fields = ["id", "name", "restaurant_name", "dishes"]
