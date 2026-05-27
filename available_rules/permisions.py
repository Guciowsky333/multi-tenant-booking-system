from rest_framework import permissions

from restaurants.models import Restaurant


class IsRestaurantRelatedOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "create":
            restaurant_id = request.data.get("restaurant")
            if not restaurant_id:
                return True
            restaurant = Restaurant.objects.filter(id=restaurant_id).first()
            if not restaurant:
                return True
            return restaurant.owner == request.user
        return True
