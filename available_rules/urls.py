from django.urls import include, path
from rest_framework.routers import DefaultRouter

from available_rules.views import AvailableRuleViewSet, RestaurantBreakViewSet, RestaurantTableViewSet

router = DefaultRouter()
router.register("restaurant_table", RestaurantTableViewSet, basename="restaurant_table")
router.register("restaurant_break", RestaurantBreakViewSet, basename="restaurant_break")
router.register("", AvailableRuleViewSet, basename="available_rules")


urlpatterns = [
    path("", include(router.urls)),
]
