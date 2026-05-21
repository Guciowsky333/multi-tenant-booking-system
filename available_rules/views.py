# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from available_rules.models import AvailableRule
from available_rules.permisions import IsRestaurantRelatedOwner
from available_rules.serializers import AvailableRuleSerializer


class AvailableRuleViewSet(viewsets.ModelViewSet):
    queryset = AvailableRule.objects.all()
    serializer_class = AvailableRuleSerializer
    permission_classes = [IsAuthenticated, IsRestaurantRelatedOwner]

    def get_queryset(self):
        return AvailableRule.objects.filter(restaurant__owner=self.request.user)
