from datetime import date
from urllib.parse import urlencode

from django.core.cache import cache
from django.db.models import Avg, FloatField, Prefetch, Value
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from available_rules.models import AvailableRule, RestaurantBreak, RestaurantTable
from booking_system.serializers import BookingSerializer
from menus.models import Menu
from restaurants.filters import RestaurantFilter
from restaurants.models import CuisineType, Restaurant
from restaurants.permissions import IsRestaurantManagerOrOwner, IsRestaurantMemberOrOwner, RestaurantPermission
from restaurants.serializers import (
    CuisineTypeSerializer,
    RestaurantBanSerializer,
    RestaurantBanSwaggerSerializer,
    RestaurantDetailSerializer,
    RestaurantSerializer,
)
from restaurants.services import (
    check_if_user_is_banned,
    create_restaurant_ban,
    get_all_bookings_per_day,
    get_available_hours_per_day,
    show_all_bans,
    unban_user,
)
from user_reviews.serializers import ReviewSerializer


class RestaurantPagination(PageNumberPagination):
    page_size = 10


class RestaurantBanPagination(PageNumberPagination):
    page_size = 20


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
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    pagination_class = RestaurantPagination

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), RestaurantPermission()]
        if self.action == "all_bookings_per_day":
            return [IsAuthenticated(), IsRestaurantMemberOrOwner()]
        if self.action in ["ban_user", "unban_user", "list_bans", "check_user"]:
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

    @extend_schema(
        summary="Shows all available restaurants",
        description="""
        Shows all available restaurants with provided filters.
        If user provides a filter that does not exist, it is ignored and all restaurants are returned.

        Business rules:
        - Allowed filters: (city, city__icontains, cuisine_type, reservation_duration_minutes).
        - Allowed ordering: "avg_rating", "-avg_rating" if user provided anything else restaurants will
        be sorted by "id"
        - If user provided page it must exist and contains restaurants.
        - Request user must be authenticated.
        """,
        parameters=[
            OpenApiParameter(name="city", required=False, description="The city where the restaurant is located"),
            OpenApiParameter(name="cuisine_type", required=False, description="The cuisine type of the restaurant"),
            OpenApiParameter(
                name="reservation_duration_minutes", required=False, description="Reservation duration minutes"
            ),
            OpenApiParameter(name="ordering", required=False, description="The ordering of the restaurants"),
        ],
        responses={
            200: OpenApiResponse(description="All available restaurants."),
            400: OpenApiResponse(
                description="Invalid data in a recognized filter, for instance a string value in reservation_duration_minutes"
            ),
            401: OpenApiResponse(description="User is not authenticated"),
            404: OpenApiResponse(description="Internal page"),
        },
    )
    def list(self, request, *args, **kwargs):

        params = request.query_params
        mutable_params = params.copy()

        allowed_filters = ["city", "city__icontains", "cuisine_type", "reservation_duration_minutes", "ordering"]

        # If any param is not in allowed_filters we do not save it in cache as cache_key
        for param in list(mutable_params.keys()):
            if param not in allowed_filters:
                mutable_params.pop(param)

        ordering = request.query_params.get("ordering")
        # If field "ordering" is anything other than "avg_rating" or "-avg_rating" sets it as "id"
        if ordering not in ["avg_rating", "-avg_rating"]:
            mutable_params.pop("ordering", None)
            ordering = "id"

        # Sorting parms because order of filters does not matter in cache key
        sorted_parms = urlencode(sorted(mutable_params.items()))

        cache_key = "restaurants_all" if not sorted_parms else f"restaurants_all_{sorted_parms}"

        # If data are in Redis we take them form there
        data = cache.get(cache_key)

        # If data are not in Redis we take them from database and then save them to Redis for 5 minutes
        if data is None:
            queryset = self.get_queryset()
            # orders queryset by avg_rating if provided, if not orders by id
            if ordering in ["avg_rating", "-avg_rating"]:
                queryset = queryset.annotate(
                    avg_rating=Coalesce(
                        Avg("reviews__rating"),
                        Value(0),
                        output_field=FloatField(),
                    )
                )
            queryset = self.filter_queryset(queryset.order_by(ordering))
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

    @extend_schema(
        summary="Returns all reviews for provided restaurant",
        description="""
        Returns all reviews for provided restaurant.
        
        Business rules:
        - Restaurant must exist.
        - Request user must be authenticated.
        - If user provided page it must exist and contains reviews.
        """,
        responses={
            200: OpenApiResponse(description="All reviews for provided restaurant."),
            401: OpenApiResponse(description="User is not authenticated"),
            404: OpenApiResponse(description="Invalid page/ Restaurant not found"),
        },
    )
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

    @extend_schema(
        summary="Returns all available hours per day.",
        description="""
        Returns all available hours when user can make a booking at provided day
        with provided amount of people (guests).

        Business rules:
        - Fields (date, guests) are required.
        - Date must be in format YYYY-MM-DD.
        - Restaurant must exist.
        - Request user must be authenticated.
        """,
        parameters=[
            OpenApiParameter(name="date", required=True, description="Date that user want to check"),
            OpenApiParameter(name="guests", required=True, description="Number of guests"),
        ],
        responses={
            200: OpenApiResponse(description="All available hours per day."),
            401: OpenApiResponse(description="User is not authenticated"),
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Restaurant not found"),
        },
    )
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

    @extend_schema(
        summary="Returns all bookings at provided date.",
        description="""
        Returns all bookings at provided date with status confirmed, completed or no_show.
        This endpoint is allowed only for members of provided restaurant for tracking 
        the schedule at provided date.
        
        Business rules:
        - If the user does not provide a date, the endpoint returns all bookings for the current day.
        - Date must be in format YYYY-MM-DD.
        - Restaurant must exist.
        - Request user must be authenticated.
        - Request user has to be member or owner of provided restaurant.
        """,
        parameters=[
            OpenApiParameter(name="date", required=False, description="Date that user want to check"),
        ],
        responses={
            200: OpenApiResponse(description="All bookings at provided date."),
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Restaurant not found"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
        },
    )
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

    @extend_schema(
        summary="Ban user",
        description="""
        Creates RestaurantBan object for provided user at provided restaurant.
        
        Business rules:
        - Request user has to be authenticated.
        - Request user has to be manager or owner of provided restaurant.
        - Field email is required.
        - User with provided email must exist.
        - Provided user cannot be banned at provided restaurant.
        """,
        request=RestaurantBanSwaggerSerializer,
        responses={
            201: OpenApiResponse(description="RestaurantBan object created correctly"),
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Restaurant not found/ User with provided email does not exist"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
        },
    )
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
                status=status.HTTP_201_CREATED,
            )
        except NotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Unban user",
        description="""
        Deletes object RestaurantBan for provided email at provided restaurant.
        
        Business rules:
        - Request user has to be authenticated.
        - Request user has to be manager or owner of provided restaurant.
        - Field email is required.
        - User with provided email must exist and be banned in provided restaurant.
        """,
        parameters=[
            OpenApiParameter(name="email", required=True, description="User email"),
        ],
        responses={
            204: OpenApiResponse(description="Deletes object RestaurantBan correctly"),
            400: OpenApiResponse(description="Provided user does not have ban in the restaurant"),
            404: OpenApiResponse(description="Restaurant not found/ User with provided email does not exist"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
        },
    )
    @action(detail=True, methods=["delete"], url_path="unban_user")
    def unban_user(self, request, pk=None):
        email = request.query_params.get("email")
        try:
            unban_user(self.get_object(), email)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except NotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Shows all bans",
        description="""
        Shows all users with ban at provided restaurant default ordering start by the older one.
        
        Business rules:
        - Request user has to be authenticated.
        - Request user has to be manager or owner of provided restaurant.
        - If the user provides the "ordering" field, only two options are allowed: "created_at" and "-created_at".
        Default = created_at
        - If user provides page this page must exist and has objects inside.
        Default page = 1 
        """,
        parameters=[
            OpenApiParameter(name="page", required=False, description="Page"),
            OpenApiParameter(name="ordering", required=False, description="Ordering field"),
        ],
        responses={
            200: OpenApiResponse(description="list all users with ban at provided restaurant"),
            400: OpenApiResponse(description="Invalid ordering field"),
            404: OpenApiResponse(description="Restaurant not found"),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
        },
    )
    @action(detail=True, methods=["get"], url_path="list_bans")
    def list_bans(self, request, pk=None):
        ordering = request.query_params.get("ordering", "created_at")
        self.pagination_class = RestaurantBanPagination
        try:
            queryset = show_all_bans(self.get_object(), ordering)
            page = self.paginate_queryset(queryset)
            serializer = RestaurantBanSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Shows RestaurantBan object for provided user",
        description="""
        Shows if user with provided email has ban at provided restaurant or not.
        
        Business rules:
        - Request user has to be authenticated.
        - Request user has to be manager or owner of provided restaurant.
        - Field email is required.
        - User with provided email must exist.
        - If provided user does not have ban return 404
        """,
        parameters=[
            OpenApiParameter(name="email", required=True, description="User email"),
        ],
        responses={
            200: OpenApiResponse(description="Shows RestaurantBan object for provided user"),
            400: OpenApiResponse(description="Field email is required"),
            404: OpenApiResponse(
                description="Restaurant not found/ User does not exist/ Provided user does not have ban"
            ),
            403: OpenApiResponse(description="User does not have permission to access this endpoint"),
            401: OpenApiResponse(description="User is not authorized"),
        },
    )
    @action(detail=True, methods=["get"], url_path="check_user")
    def check_user(self, request, pk=None):
        email = request.query_params.get("email")
        try:
            user_ban = check_if_user_is_banned(self.get_object(), email)
            serializer = RestaurantBanSerializer(user_ban)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except NotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
