from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from restaurants.models import CuisineType, Restaurant
from restaurants.permisions import IsRestaurantOwner
from restaurants.serializers import CuisineTypeSerializer, RestaurantSerializer


# Create your views here.
class AllCuisinesTypeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Shows all available cuisines",
        description="""
        Shows all available cuisines.
        """,
        responses={
            200: OpenApiResponse(description="All available cuisines."),
            401: OpenApiResponse(description="Unauthorized"),
        },
    )
    def get(self, request):
        queryset = CuisineType.objects.all()
        serializer = CuisineTypeSerializer(queryset, many=True)
        return Response({"message": "All allowed cuisines types", "cuisine_types": serializer.data}, status=200)


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]

    def get_permissions(self):
        """
        Destroy or update restaurants is allowed only by owner of that restaurants.
        Create or get all restaurants is allowed by any log in users
        """
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsRestaurantOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """
        User who create a new restaurant has become owner of the restaurant.
        """
        serializer.save(owner=self.request.user)

    @extend_schema(
        summary="Returns all list of restaurants",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get restaurant details",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="create restaurant",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="update restaurant",
        description="""
        Business rules:
        - Only for owner of restaurant.
        """,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partial update restaurant",
        description="""
        Business rules:
        - Only for owner of restaurant.
        """,
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="destroy restaurant",
        description="""
        Business rules:
        - Only for owner of restaurant.
        """,
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
