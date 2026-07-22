from rest_framework import permissions

from memberships.models import MemberShip


class IsMemberOfRestaurant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Returns 200 only for members of the restaurant on which the booking belongs or for owner this restaurant.

        Using in "change_status_completed" and "change_status_no_show" actions
        """
        return (
            obj.restaurant.owner == request.user
            or MemberShip.objects.filter(restaurant=obj.restaurant, user=request.user).exists()
        )


class IsMemberOfRestaurantOrOwnerOfBooking(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Returns 200 for members of the restaurant on which the booking belongs or for the owner of the booking.

        Using in "change_status_cancelled" action
        """
        return (
            obj.user == request.user
            or obj.restaurant.owner == request.user
            or MemberShip.objects.filter(restaurant=obj.restaurant, user=request.user).exists()
        )
