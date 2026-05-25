# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from available_rules.models import AvailableRule, RestaurantTable
from available_rules.permisions import IsRestaurantRelatedOwner
from available_rules.serializers import AvailableRuleSerializer, RestaurantTableSerializer


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
