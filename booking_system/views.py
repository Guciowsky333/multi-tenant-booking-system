# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from booking_system.models import Booking
from booking_system.serializers import BookingDetailsSerializer, BookingSerializer


class BookingViewSet(ModelViewSet):
    http_method_names = ["get", "post"]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookingDetailsSerializer
        return BookingSerializer
