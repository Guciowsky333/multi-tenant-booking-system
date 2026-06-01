import django_filters

from restaurants.models import Restaurant


class RestaurantFilter(django_filters.FilterSet):
    class Meta:
        model = Restaurant
        fields = {
            "city": ["exact", "icontains"],
            "cuisine_type": ["exact"],
            "reservation_duration_minutes": ["exact"],
        }
