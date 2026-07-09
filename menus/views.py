from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from menus.models import Dish, Menu
from menus.permisions import IsRestaurantOwnerOrManager
from menus.serializers import DishSerializer, MenuSerializer

# Create your views here.


class DishViewSet(viewsets.ModelViewSet):
    """
    Endpoint for managing dishes. List and retrieve are not available here.
    To see all dishes in a menu see GET /api/menus/{id}/
    """

    http_method_names = ["post", "delete", "patch"]
    serializer_class = DishSerializer
    queryset = Dish.objects.all()
    permission_classes = [IsAuthenticated, IsRestaurantOwnerOrManager]


class MenuViewSet(RetrieveModelMixin, UpdateModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    Methods post, patch, delete are only for allowed persons.
    List and put are not available here.
    Retrieve is allowed for each user to see all dishes inside menu allowed filter by price.
    See GET /api/restaurants/{restaurant_id}/ to see all menus available in a restaurant.
    """

    serializer_class = MenuSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Menu.objects.prefetch_related("dishes")
    permission_classes = [IsAuthenticated, IsRestaurantOwnerOrManager]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                required=False,
                description="Order dishes by price. Use 'price' for ascending, '-price' for descending.",
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
