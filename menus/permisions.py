from rest_framework import permissions

from memberships.models import MemberShip
from menus.models import Menu
from restaurants.models import Restaurant


class IsRestaurantOwnerOrManager(permissions.BasePermission):
    """
    This permission applies to both DishViewSet and MenuViewSet.
    Only owner or manager of the restaurant can create, update or delete menus or dishes inside restaurant
    """

    def has_permission(self, request, view):
        if view.action == "create":
            restaurant_id = request.data.get("restaurant")
            menu_id = request.data.get("menu")

            # If the user does not provide any of these fields, the serializer will return a 404
            if not restaurant_id and not menu_id:
                return True

            if menu_id:
                # Menu_id means that user want to create a Dish model
                menu = Menu.objects.filter(id=menu_id).first()
                # If user provided wrong id serializer will return 404
                if not menu:
                    return True
                restaurant = menu.restaurant
            if restaurant_id:
                # Restaurant_id means that user want to create a Menu model
                restaurant = Restaurant.objects.filter(id=restaurant_id).first()
                if not restaurant:
                    return True

            return (
                restaurant.owner == request.user
                or MemberShip.objects.filter(user=request.user, restaurant=restaurant, role="manager").exists()
            )
        return True

    def has_object_permission(self, request, view, obj):
        # Take restaurant from the Menu or Dish model
        restaurant = obj.restaurant if hasattr(obj, "restaurant") else obj.menu.restaurant
        return (
            restaurant.owner == request.user
            or MemberShip.objects.filter(user=request.user, restaurant=restaurant, role="manager").exists()
        )
