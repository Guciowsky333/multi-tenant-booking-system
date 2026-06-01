from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from restaurants.filters import RestaurantFilter
from restaurants.models import CuisineType, Restaurant
from restaurants.permisions import IsRestaurantManagerOrOwner
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = RestaurantFilter
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    parser_classes = [FormParser, MultiPartParser]

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsRestaurantManagerOrOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """
        User who create a new restaurant has become owner of the restaurant.
        """
        serializer.save(owner=self.request.user)
