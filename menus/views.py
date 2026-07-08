from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from menus.models import Dish
from menus.permisions import IsRestaurantOwnerOrManager
from menus.serializers import DishSerializer

# Create your views here.


class DishViewSet(viewsets.ModelViewSet):
    """
    Endpoint for managing dishes. List and retrieve are not available here.
    To see all dishes in a menu see GET /api/menus/{id}/
    """

    http_method_names = ["post", "delete", "patch"]
    serializer_class = DishSerializer
    queryset = Dish.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsRestaurantOwnerOrManager]
