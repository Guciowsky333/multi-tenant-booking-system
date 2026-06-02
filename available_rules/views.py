# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from available_rules.models import AvailableRule, RestaurantBreak, RestaurantException, RestaurantTable
from available_rules.permisions import IsRestaurantOwnerOrManager, IsRestaurantRelatedOwner
from available_rules.serializers import (
    AvailableRuleSerializer,
    RestaurantBreakSerializer,
    RestaurantExceptionSerializer,
    RestaurantTableSerializer,
)


class AvailableRuleViewSet(viewsets.ModelViewSet):
    """
    This endpoint is allowed only for owner or members of the restaurant.
    For public available rules date use GET /api/restaurants/{id}/ which returns available rules
    assigned to provided restaurant.
    """

    serializer_class = AvailableRuleSerializer
    permission_classes = [IsAuthenticated, IsRestaurantOwnerOrManager]

    def get_queryset(self):
        return AvailableRule.objects.filter(restaurant__owner=self.request.user) | AvailableRule.objects.filter(
            restaurant__memberships__user=self.request.user
        )


class RestaurantTableViewSet(viewsets.ModelViewSet):
    """
    The same access rules as AvailableRuleViewSet.
    For public data use GET /api/restaurants/{id}/
    """

    serializer_class = RestaurantTableSerializer
    permission_classes = [IsAuthenticated, IsRestaurantOwnerOrManager]

    def get_queryset(self):
        return RestaurantTable.objects.filter(restaurant__owner=self.request.user) | RestaurantTable.objects.filter(
            restaurant__memberships__user=self.request.user
        )


class RestaurantBreakViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantBreakSerializer
    permission_classes = [IsAuthenticated, IsRestaurantRelatedOwner]

    def get_queryset(self):
        return RestaurantBreak.objects.filter(restaurant__owner=self.request.user)


class RestaurantExceptionViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantExceptionSerializer
    permission_classes = [IsAuthenticated, IsRestaurantRelatedOwner]

    def get_queryset(self):
        return RestaurantException.objects.filter(restaurant__owner=self.request.user)
