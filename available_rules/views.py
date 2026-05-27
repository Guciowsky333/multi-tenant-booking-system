# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from available_rules.models import AvailableRule, RestaurantBreak, RestaurantException, RestaurantTable
from available_rules.permisions import IsRestaurantRelatedOwner
from available_rules.serializers import (
    AvailableRuleSerializer,
    RestaurantBreakSerializer,
    RestaurantExceptionSerializer,
    RestaurantTableSerializer,
)


class AvailableRuleViewSet(viewsets.ModelViewSet):
    serializer_class = AvailableRuleSerializer
    permission_classes = [IsAuthenticated, IsRestaurantRelatedOwner]

    def get_queryset(self):
        return AvailableRule.objects.filter(restaurant__owner=self.request.user)


class RestaurantTableViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantTableSerializer
    permission_classes = [IsAuthenticated, IsRestaurantRelatedOwner]

    def get_queryset(self):
        return RestaurantTable.objects.filter(restaurant__owner=self.request.user)


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
