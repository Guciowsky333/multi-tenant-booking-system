from datetime import time, timedelta

import pytest

from booking_system.models import Booking
from booking_system.tests.test_endpoints import next_monday


@pytest.fixture
def test_booking_1(db, test_user_2, test_restaurant, test_restaurant_table):
    return Booking.objects.create(
        restaurant=test_restaurant,
        table=test_restaurant_table,
        user=test_user_2,
        date=next_monday() + timedelta(days=7),
        start_time=time(15, 0, 0),
    )


@pytest.fixture
def test_booking_2(db, test_user_2, test_restaurant, test_restaurant_table):
    return Booking.objects.create(
        restaurant=test_restaurant,
        table=test_restaurant_table,
        user=test_user_2,
        date=next_monday(),
        start_time=time(17, 0, 0),
    )
