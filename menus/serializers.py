from rest_framework import serializers

from menus.models import Dish, Menu


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ["id", "menu", "name", "price", "description", "image"]

    def validate_menu(self, value):
        if self.instance and self.instance.menu != value:
            raise serializers.ValidationError("Cannot change menu of already existing dish")
        return value


class MenuSerializer(serializers.ModelSerializer):
    dishes = serializers.SerializerMethodField()
    restaurant_name = serializers.SerializerMethodField()

    def get_restaurant_name(self, obj):
        return obj.restaurant.name

    def get_dishes(self, obj):
        ordering = self.context["request"].query_params.get("ordering", "price")
        if ordering not in ["price", "-price"]:
            raise serializers.ValidationError("Invalid ordering")

        dishes = obj.dishes.order_by(ordering)
        serializer = DishSerializer(dishes, many=True)
        return serializer.data

    class Meta:
        model = Menu
        fields = ["id", "name", "restaurant", "restaurant_name", "dishes"]

    def validate_restaurant(self, value):
        if self.instance and self.instance.restaurant != value:
            raise serializers.ValidationError("Cannot change restaurant of already existing menu")
        return value


class MenuBriefSerializer(serializers.ModelSerializer):
    """
    This serializer is used in GET /api/restaurants/{restaurant_id} to display all menus
    in the restaurant.
    """

    class Meta:
        model = Menu
        fields = ["id", "name"]
