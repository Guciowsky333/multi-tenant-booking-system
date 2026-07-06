from urllib.parse import urlencode

from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from restaurants.filters import RestaurantFilter
from restaurants.models import CuisineType, Restaurant
from restaurants.permisions import IsRestaurantManagerOrOwner
from restaurants.serializers import CuisineTypeSerializer, RestaurantSerializer


class RestaurantPagination(PageNumberPagination):
    page_size = 10


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
    queryset = Restaurant.objects.all().order_by("id")
    serializer_class = RestaurantSerializer
    parser_classes = [FormParser, MultiPartParser]
    pagination_class = RestaurantPagination

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsRestaurantManagerOrOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """
        User who create a new restaurant has become owner of the restaurant.
        """
        serializer.save(owner=self.request.user)

        # Cleaning our Redis to add new restaurant
        cache.delete_pattern("restaurants_all*")

    def perform_update(self, serializer):
        serializer.save()

        # Cleaning Redis if someone changed something inside a restaurant
        cache.delete_pattern("restaurants_all*")

    def perform_destroy(self, instance):
        instance.delete()

        # Cleaning Redis if someone deleted his restaurant
        cache.delete_pattern("restaurants_all*")

    def list(self, request, *args, **kwargs):
        params = request.query_params

        # Sorting parms because order of filters does not matter in cache key
        sorted_parms = urlencode(sorted(params.items()))

        cache_key = "restaurants_all" if not sorted_parms else f"restaurants_all_{sorted_parms}"

        # If data are in Redis we take them form there
        data = cache.get(cache_key)

        if data is None:
            # If data are not in Redis we take them from database and then save them to Redis for 5 minutes
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)

            # Save metadata to cache
            data = {
                "count": self.paginator.page.paginator.count,
                "next": self.paginator.get_next_link(),
                "previous": self.paginator.get_previous_link(),
                "results": serializer.data,
            }

            cache.set(cache_key, data, timeout=300)

        return Response(data)
