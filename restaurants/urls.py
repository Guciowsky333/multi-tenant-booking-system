from django.urls import include, path
from rest_framework.routers import DefaultRouter

from restaurants.views import AllCuisinesTypeView, RestaurantViewSet

router = DefaultRouter()
router.register("", RestaurantViewSet, basename="restaurant")

urlpatterns = [
    path("all_cuisine_type/", AllCuisinesTypeView.as_view(), name="all_cuisine_type"),
    path("", include(router.urls)),
]
