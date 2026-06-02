from rest_framework import permissions

from memberships.models import MemberShip
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


class IsRestaurantOwnerOrManager(permissions.BasePermission):
    """
    - create, update, partial_update, destroy: Only owner or member with "manager" role.
    - retrieve, List: Handled by IsAuthenticated in get_permissions.

    Note: Returns 403 instead of 404 for non-existent restaurants intentionally
    to avoid exposing whether a restaurant exists.
    """

    def has_object_permission(self, request, view, obj):
        return (
            obj.restaurant.owner == request.user
            or MemberShip.objects.filter(restaurant=obj.restaurant, user=request.user, role="manager").exists()
        )

    def has_permission(self, request, view):
        if view.action == "create":
            restaurant_id = request.data.get("restaurant")
            # If user did not provide restaurant serializer will return 400 error
            if not restaurant_id:
                return True
            is_owner = Restaurant.objects.filter(id=restaurant_id, owner=request.user).exists()
            is_manager_member = MemberShip.objects.filter(
                restaurant=restaurant_id, user=request.user, role="manager"
            ).exists()
            return is_owner or is_manager_member
        return True
