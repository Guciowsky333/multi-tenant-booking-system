# Create your views here.
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from memberships.models import MemberShip
from memberships.permisions import IsRestaurantOwner
from memberships.serializers import MemberShipSerializer, MembershipUpdateSerializer


class MemberShipViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    def get_queryset(self):
        return MemberShip.objects.all()

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return MembershipUpdateSerializer
        return MemberShipSerializer

    @extend_schema(
        summary="Returns list of member in provided restaurant",
        description="""
        Returns list of member in provided restaurant.
        
        business rules:
        - Filed restaurant_id is required
        - Restaurant with provided id must exist
        - Request user must be authenticated
        - Request user must be member of the restaurant
        """,
        parameters=[OpenApiParameter(name="restaurant_id", type=int, required=True)],
        responses={
            200: OpenApiResponse(description="List of all members of the restaurant"),
            400: OpenApiResponse(description="User did not provide restaurant"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
        },
    )
    def list(self, request, *args, **kwargs):
        restaurant_id = request.query_params.get("restaurant_id")
        if not restaurant_id:
            return Response({"message": "Field restaurant is required"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = MemberShip.objects.filter(restaurant=restaurant_id)
        serializer = MemberShipSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create new membership",
        description="""
        Create membership with provided email at provided restaurant.
        
        Business rules:
        - Field (restaurant, email, role) are required.
        - Restaurant must exist.
        - In body you should provide email instead of user_id. The 
        serializer will automatically find the user with this email.
        - User with provided email must exist and cannot be owner of provided restaurant
        - Combination of restaurant and user must be unique (One user can have max 1 membership)
        - Allowed role values : "manager", "staff".
        - Request user must be authenticated.
        - Request user must be owner of the restaurant.
        """,
        request=MemberShipSerializer,
        responses={
            201: OpenApiResponse(description="Membership created"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update membership role",
        description="""
        Updates role of existing membership.
        Only 'role' field can be changed - restaurant and user cannot be modified after creation.

        Business rules:
        - Field role is required.
        - Allowed role values: "manager", "staff".
        - Request user must be authenticated.
        - Request user must be owner of the restaurant.
        """,
        request=MembershipUpdateSerializer,
        responses={
            200: OpenApiResponse(description="Membership updated"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
            404: OpenApiResponse(description="Membership not found"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially updates membership role",
        description="""
        The same business rules as in update.
        """,
        request=MembershipUpdateSerializer,
        responses={
            200: OpenApiResponse(description="Membership updated"),
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
            404: OpenApiResponse(description="Membership not found"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
