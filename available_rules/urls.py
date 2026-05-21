from django.urls import include, path
from rest_framework.routers import DefaultRouter

from available_rules.views import AvailableRuleViewSet

router = DefaultRouter()
router.register("", AvailableRuleViewSet, basename="available_rules")
urlpatterns = [
    path("", include(router.urls)),
]
