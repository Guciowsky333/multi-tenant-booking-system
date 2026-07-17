# Create your views here.
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from booking_system.models import Booking
from booking_system.permisions import IsMemberOfRestaurant
from booking_system.serializers import BookingDetailsSerializer, BookingSerializer
from booking_system.services import (
    change_booking_status_to_completed,
    change_booking_status_to_confirmed,
    create_booking,
)
from booking_system.tasks import cancelled_booking_after_30_minutes, send_booking_confirmation_email


class BookingPagination(PageNumberPagination):
    page_size = 10


class BookingViewSet(ModelViewSet):
    http_method_names = ["get", "post"]
    permission_classes = [IsAuthenticated]
    pagination_class = BookingPagination

    def get_queryset(self):
        if self.action == "change_status_completed":
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user).order_by("date", "start_time")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookingDetailsSerializer
        return BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        restaurant = serializer.validated_data["restaurant"]
        date = serializer.validated_data["date"]
        start_time = serializer.validated_data["start_time"]
        guests = serializer.validated_data["guests"]

        try:
            booking = create_booking(restaurant, date, start_time, guests, user=self.request.user)
            serializer.validated_data.pop("guests")

            # Sending email to user to confirm booking
            send_booking_confirmation_email.delay(self.request.user.email, booking.confirmation_token)
            # After 30 minutes booking will change its status to "CANCELLED" if user does not confirm it
            cancelled_booking_after_30_minutes.apply_async(args=[booking.id], countdown=1800)

            return Response(
                {
                    "message": """
                Booking has been created successfully.
                
                We sends to you link to confirm your booking on your email.
                This link will be valid for 30 minutes.
                """
                },
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Change status from pending to confirmed.",
        description="""
               Changes the status of the booking from pending to confirmed by confirmation_token.

               Business rules:
               - Every user has access to this endpoint, even without logging in, provided they supply a valid `confirmation_token`.
               - Provided confirmation_token must belong to exist booking.
               - Status of the booking must be pending only then you can change it to confirmed.
               - User has 30 minutes to do that after that time celery task will change its status to cancelled.
               """,
        parameters=[
            OpenApiParameter(name="token", required=True, description="confirmation_token of the booking"),
        ],
    )
    @action(detail=False, methods=["get"], url_path="status_confirmed", permission_classes=[AllowAny])
    def change_status_confirmed(self, request):
        token = request.query_params.get("token")
        try:
            change_booking_status_to_confirmed(token)
            return Response({"status": "Status has been changed correctly"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except NotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Change status from confirmed to completed.",
        description="""
        Changes the status of the booking from confirmed to completed.
        
        When user finished his booking members of the restaurant can change its status to completed.
        So that the reservation doesn't keep the table occupied.
        
        Business rules:
        - Request user has to be authenticated.
        - Request user has to be member of the restaurant to which booking belongs.
        - Provided booking must exist.
        - Provided booking must has status "confirmed".
        """,
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="status_completed",
        permission_classes=[IsAuthenticated, IsMemberOfRestaurant],
    )
    def change_status_completed(self, request, pk=None):
        try:
            change_booking_status_to_completed(self.get_object())
            return Response({"status": "Status has been changed correctly"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
