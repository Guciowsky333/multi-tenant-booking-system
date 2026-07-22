from datetime import date
from urllib.parse import urlencode

from django.core.cache import cache
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from available_rules.models import AvailableRule, RestaurantBreak, RestaurantTable
from booking_system.serializers import BookingSerializer
from menus.models import Menu
from restaurants.filters import RestaurantFilter
from restaurants.models import CuisineType, Restaurant
from restaurants.permissions import IsRestaurantManagerOrOwner, IsRestaurantMemberOrOwner, RestaurantPermission
from restaurants.serializers import CuisineTypeSerializer, RestaurantDetailSerializer, RestaurantSerializer
from restaurants.services import create_restaurant_ban, get_all_bookings_per_day, get_available_hours_per_day
from user_reviews.serializers import ReviewSerializer


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
    serializer_class = RestaurantSerializer
    parser_classes = [FormParser, MultiPartParser]
    pagination_class = RestaurantPagination

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), RestaurantPermission()]
        if self.action == "all_bookings_per_day":
            return [IsAuthenticated(), IsRestaurantMemberOrOwner()]
        if self.action == "ban_user":
            return [IsAuthenticated(), IsRestaurantManagerOrOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.action == "retrieve":
            return Restaurant.objects.prefetch_related(
                Prefetch("menus", queryset=Menu.objects.order_by("id")),
                Prefetch("available_rules", queryset=AvailableRule.objects.order_by("day_of_week")),
                Prefetch("restaurant_breaks", queryset=RestaurantBreak.objects.order_by("day_of_week")),
                Prefetch("restaurant_tables", queryset=RestaurantTable.objects.order_by("seats")),
            ).order_by("id")
        return Restaurant.objects.order_by("id")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RestaurantDetailSerializer
        return RestaurantSerializer

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

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="reviews")
    def reviews(self, request, pk=None):
        page_number = request.query_params.get("page", 1)
        cache_key = f"restaurant_{pk}_reviews_page_{page_number}"
        data = cache.get(cache_key)
        # If data are in cache we take them form there
        # If data with our cache_key are empty we take them form database and then set in cache
        if data is None:
            restaurant = self.get_object()
            all_reviews = restaurant.reviews.order_by("-created_at")
            page = self.paginate_queryset(all_reviews)
            serializer = ReviewSerializer(page, many=True)
            # Store metadata alongside results to preserve pagination info in cache
            data = {
                "count": self.paginator.page.paginator.count,
                "next": self.paginator.get_next_link(),
                "previous": self.paginator.get_previous_link(),
                "results": serializer.data,
            }
            cache.set(cache_key, data, timeout=300)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="available_hours")
    def available_hours_per_day(self, request, pk=None):
        provided_date = request.query_params.get("date")
        guests = request.query_params.get("guests")
        try:
            all_available_hours = get_available_hours_per_day(self.get_object(), provided_date, guests)
            return Response(
                {
                    "date": provided_date,
                    "all_available_hours": all_available_hours,
                },
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="all_bookings")
    def all_bookings_per_day(self, request, pk=None):

        provided_date = request.query_params.get("date", str(date.today()))
        try:
            all_bookings = get_all_bookings_per_day(self.get_object(), provided_date)
            serializer = BookingSerializer(all_bookings, many=True)
            return Response(
                {
                    "date": provided_date,
                    "all_bookings": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="ban_user")
    def ban_user(self, request, pk=None):
        email = request.data.get("email")
        description = request.data.get("description")
        try:
            create_restaurant_ban(self.get_object(), email, description)
            return Response(
                {
                    "message": "User has been banned",
                },
                status=status.HTTP_200_OK,
            )
        except NotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
