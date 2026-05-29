from rest_framework import permissions

from memberships.models import MemberShip
from restaurants.models import Restaurant


class IsRestaurantOwner(permissions.BasePermission):
    """
    - create: Only owner of restaurant can add new members
    - retrieve, update, partial_update, destroy: Only restaurant owner
    - list: Only members of the restaurant
    """

    def has_object_permission(self, request, view, obj):
        return request.user == obj.restaurant.owner

    def has_permission(self, request, view):
        if view.action == "create":
            restaurant_id = request.data.get("restaurant")
            # If user did not provide restaurant_id serializer will return 400 error
            if not restaurant_id:
                return True
            return Restaurant.objects.filter(id=restaurant_id, owner=request.user).exists()
        if view.action == "list":
            restaurant_id = request.query_params.get("restaurant_id")
            # If user did not provide restaurant_id view will return 400 error
            if not restaurant_id:
                return True
            # Owner of the restaurant
            is_owner = Restaurant.objects.filter(id=restaurant_id, owner=request.user).exists()
            # Member of the restaurant
            is_member = MemberShip.objects.filter(restaurant=restaurant_id, user=request.user).exists()
            return is_owner or is_member
        return True
