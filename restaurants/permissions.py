from rest_framework import permissions

from memberships.models import MemberShip


class RestaurantPermission(permissions.BasePermission):
    """
    - create, list, retrieve: All log in users
    - update, partial_update: Only owner of restaurant or member with role = "manager"
    - destroy: Only owner of restaurant
    """

    def has_object_permission(self, request, view, obj):

        if view.action == "destroy":
            return request.user == obj.owner
        is_owner = request.user == obj.owner
        is_manager_member = MemberShip.objects.filter(
            restaurant=obj, user=request.user, role=MemberShip.Role.MANAGER
        ).exists()
        return is_owner or is_manager_member


class IsRestaurantMemberOrOwner(permissions.BasePermission):
    """
    Returns 200 for members or owner of provided restaurant.

    Used in all_bookings_per_day action
    """

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or MemberShip.objects.filter(restaurant=obj, user=request.user).exists()


class IsRestaurantManagerOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        restaurant = view.get_object()
        return (
            restaurant.owner == request.user
            or MemberShip.objects.filter(
                restaurant=restaurant, user=request.user, role=MemberShip.Role.MANAGER
            ).exists()
        )
