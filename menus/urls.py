from django.urls import include, path
from rest_framework.routers import DefaultRouter

from menus.views import DishViewSet, MenuViewSet

router = DefaultRouter()
router.register("dish", DishViewSet, basename="dish")
router.register("", MenuViewSet, basename="menus")

urlpatterns = [
    path("", include(router.urls)),
]
