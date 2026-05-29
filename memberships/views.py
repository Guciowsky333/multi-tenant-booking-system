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
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
        },
    )
    def list(self, request, *args, **kwargs):
        restaurant_id = request.query_params.get("restaurant_id")
        if not restaurant_id:
            return Response({"message": "Field restaurant is required"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = MemberShip.objects.filter(restaurant=restaurant_id)
        serializer = MemberShipSerializer(queryset, many=True)
        return Response(serializer.data)
