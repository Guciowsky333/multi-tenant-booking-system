from django.urls import include, path
from rest_framework.routers import DefaultRouter

from memberships.views import MemberShipViewSet

router = DefaultRouter()

router.register("", MemberShipViewSet, basename="memberships")

urlpatterns = [
    path("", include(router.urls)),
]
