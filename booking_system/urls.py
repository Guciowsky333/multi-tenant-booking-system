from django.urls import include, path
from rest_framework.routers import DefaultRouter

from booking_system.views import BookingViewSet

router = DefaultRouter()
router.register("", BookingViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
