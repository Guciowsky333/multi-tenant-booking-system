from rest_framework import permissions

from memberships.models import MemberShip


class IsMemberOfRestaurant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Only member of the restaurant to which the booking belongs are able to change its status
        to completed
        """
        return (
            obj.restaurant.owner == request.user
            or MemberShip.objects.filter(restaurant=obj.restaurant, user=request.user).exists()
        )
