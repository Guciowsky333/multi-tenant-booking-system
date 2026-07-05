from rest_framework import permissions

from memberships.models import MemberShip


class IsReviewOwnerOrRestaurantOwnerOrManager(permissions.BasePermission):
    """
    - create, list, retrieve: All log in users
    - update, partial_update: Only owner of review
    - destroy: Owner of review and owner or manager of the restaurant
    """

    def has_object_permission(self, request, view, obj):
        if view.action == "destroy":
            return (
                obj.user == request.user
                or obj.restaurant.owner == request.user
                or MemberShip.objects.filter(restaurant=obj.restaurant, user=request.user, role="manager").exists()
            )
        return obj.user == request.user
