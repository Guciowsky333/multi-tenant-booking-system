from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from menus.models import Dish, Menu
from menus.permisions import MenuAndDishPermission
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
    permission_classes = [IsAuthenticated, MenuAndDishPermission]

    @extend_schema(
        summary="Create new dish",
        description="""
        Create a new dish at provided menu.
        This whole endpoint is designed for owners or managers of restaurants to
        create new dishes at their restaurants.
        
        Business rules:
        - Fields (name, menu, price) are required, optional fields (image, description).
        - Menu must exist.
        - Request user must be authenticated.
        - Request user has to be owner or manager of the restaurant to which the provided menu belongs.
        """,
        request=DishSerializer,
        responses={
            201: OpenApiResponse(description="Dish created successfully."),
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update dish",
        description="""
        Partially updates dish at provided menu.
        Only fields (name, price, image, description) can be changed - menu cannot be modified after creation.
        This endpoint is designed for owners or managers of restaurants to update dishes at their restaurants.

        Business rules:
        - Menu field cannot be changed to a different menu.
        - Request user must be authenticated.
        - Request user has to be owner or manager of the restaurant to which the provided menu belongs.
        """,
        request=DishSerializer,
        responses={
            200: OpenApiResponse(description="Dish updated successfully."),
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
            404: OpenApiResponse(description="Dish not found"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


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
    permission_classes = [IsAuthenticated, MenuAndDishPermission]

    @extend_schema(
        summary="Returns details of provided menu",
        description="""
        Returns details of provided menu and all dishes sorted by price.
        Method retrieve is allowed for every authenticated user to see all dishes in provided menu.
        To see all menus in a restaurant see GET /api/restaurants/{restaurant_id}/.
        
        Business rules:
        - Provided menu must exist.
        - Allowed ordering by price. Allowed values: "price", "-price" .
        - Request user must be Authenticated .
        """,
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                required=False,
                description="Order dishes by price. Use 'price' for ascending, '-price' for descending.",
            )
        ],
        responses={
            200: OpenApiResponse(description="Menu details"),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="User is not authorized"),
            404: OpenApiResponse(description="Menu not found"),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Creates menu at provided restaurant",
        description="""
        Creates menu at provided restaurant.
        Method create is allowed only for owner or manager of provided restaurant.
        
        Business rules:
        - Fields (restaurant, name) are required.
        - Restaurant must exist.
        - Request user must be authenticated.
        - Request user has to be owner or manager of the restaurant.
        """,
        request=MenuSerializer,
        responses={
            201: OpenApiResponse(description="Menu created"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update menu",
        description="""
        Partially updates menu at provided restaurant.
        Only 'name' field can be changed - restaurant cannot be modified after creation.
        Method partial_update is allowed only for owner or manager of provided restaurant.

        Business rules:
        - Restaurant field cannot be changed to a different restaurant.
        - Request user must be authenticated.
        - Request user has to be owner or manager of the restaurant.
        """,
        request=MenuSerializer,
        responses={
            200: OpenApiResponse(description="Menu updated"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
            404: OpenApiResponse(description="Menu not found"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
