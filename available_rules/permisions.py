from rest_framework import permissions

from memberships.models import MemberShip
from restaurants.models import Restaurant


class IsRestaurantOwnerOrManager(permissions.BasePermission):
    """
    - create, update, partial_update, destroy: Only owner or member with "manager" role.
    - retrieve, List: Only member or owner of the restaurant.

    Note: Returns 403 instead of 404 for non-existent restaurants intentionally
    to avoid exposing whether a restaurant exists.
    """

    def has_object_permission(self, request, view, obj):
        if view.action == "retrieve":
            return (
                obj.restaurant.owner == request.user
                or MemberShip.objects.filter(restaurant=obj.restaurant, user=request.user).exists()
            )
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
