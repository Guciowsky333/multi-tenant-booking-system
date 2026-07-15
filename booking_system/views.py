# Create your views here.
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from booking_system.models import Booking
from booking_system.serializers import BookingDetailsSerializer, BookingSerializer
from booking_system.services import create_booking


class BookingViewSet(ModelViewSet):
    http_method_names = ["get", "post"]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

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
            create_booking(restaurant, date, start_time, guests, user=self.request.user)
            serializer.validated_data.pop("guests")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
