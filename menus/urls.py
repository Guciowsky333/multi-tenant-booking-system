from django.urls import include, path
from rest_framework.routers import DefaultRouter

from menus.views import DishViewSet

router = DefaultRouter()
router.register("dish", DishViewSet, basename="dish")

urlpatterns = [
    path("", include(router.urls)),
]
