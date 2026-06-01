from rest_framework import permissions

from memberships.models import MemberShip


class IsRestaurantManagerOrOwner(permissions.BasePermission):
    """
    - create, list, retrieve: All log in users
    - update, partial_update: Only owner of restaurant or member with role = "manager"
    - destroy: Only owner of restaurant
    """

    def has_object_permission(self, request, view, obj):

        if view.action == "destroy":
            return request.user == obj.owner
        is_owner = request.user == obj.owner
        is_manager_member = MemberShip.objects.filter(restaurant=obj, user=request.user, role="manager").exists()
        return is_owner or is_manager_member
