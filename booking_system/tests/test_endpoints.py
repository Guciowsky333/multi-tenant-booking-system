from datetime import date, timedelta

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from booking_system.models import Booking


def next_monday():
    """
    Returns date of the next Monday.
    Test_available_rule in our test_restaurant in set on monday so in fild date we will use this function
    """
    today = date.today()
    days_until_next_monday = (6 - today.weekday()) + 1
    return today + timedelta(days=days_until_next_monday)


def test_BookingViewSet_post(test_user, test_restaurant, test_available_rule, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(user=test_user)

    body = {
        "restaurant": test_restaurant.id,
        "guests": 4,  # <-- test_restaurant_table has exactly 4 seats
        "date": next_monday(),
        "start_time": "17:00:00",
    }

    response = client.post("/api/bookings/", body)
    assert response.status_code == 201
    assert Booking.objects.filter(restaurant=test_restaurant, user=test_user, date=body["date"]).exists()


def test_BookingViewSet_post_restaurant_does_not_have_available_rules(
    test_user, test_restaurant, test_restaurant_table
):
    """
    In this test we set up date at tuesday and test_restaurant does not have model available_rule at that day.
    Endpoint should return 400 error "Restaurant is not open on provided day".
    """

    client = APIClient()
    client.force_authenticate(user=test_user)
    body = {
        "restaurant": test_restaurant.id,
        "guests": 4,
        "date": next_monday() + timedelta(days=1),
        "start_time": "17:00:00",
    }

    response = client.post("/api/bookings/", body)
    assert response.status_code == 400
    assert response.data["error"] == "Restaurant is not open on provided day"


@pytest.mark.parametrize(
    "start_time, excepted_status",
    [
        # restaurant is open to 20:00:00 in this test
        ("21:00:00", status.HTTP_400_BAD_REQUEST),
        # The booking end time extends beyond the restaurant's closing time.
        ("19:00:00", status.HTTP_400_BAD_REQUEST),
        # Correct time
        ("11:00:00", status.HTTP_201_CREATED),
    ],
)
def test_BookingViewSet_post_respects_special_hours_exception(
    start_time,
    excepted_status,
    test_user,
    test_restaurant,
    test_exception_special_hours,
    test_available_rule,
    test_restaurant_table,
):
    """
    Test that special opening hours override regular available rules.

    The restaurant is normally open from 08:00:00 to 22:00:00 according to
    AvailableRule. However, the requested booking date has a special opening
    hours exception configured, which changes the opening hours to 10:00:00-20:00:00.

    The endpoint should validate bookings against the exception hours instead of
    the regular weekly schedule.
    """
    client = APIClient()
    client.force_authenticate(user=test_user)

    body = {
        "restaurant": test_restaurant.id,
        "guests": 4,  # <-- test_restaurant_table has exactly 4 seats
        "date": test_exception_special_hours.date,
        "start_time": start_time,
    }

    response = client.post("/api/bookings/", body)
    assert response.status_code == excepted_status
    if excepted_status == status.HTTP_201_CREATED:
        assert Booking.objects.filter(restaurant=test_restaurant, user=test_user, date=body["date"]).exists()


def test_BookingViewSet_post_respects_closed_exception(
    test_user, test_restaurant, test_available_rule, test_restaurant_table, test_exception_closed
):
    """
    In provide date restaurant has exception model and in that day restaurant is closed.
    We except that endpoint override regular available rules at that day.
    """
    client = APIClient()
    client.force_authenticate(user=test_user)
    body = {
        "restaurant": test_restaurant.id,
        "guests": 4,
        "date": test_exception_closed.date,
        "start_time": "17:00:00",
    }
    response = client.post("/api/bookings/", body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "In provided date restaurant is closed"


def test_BookingViewSet_post_start_time_overlap_restaurant_break(
    test_user, test_restaurant, test_restaurant_table, test_restaurant_break, test_available_rule
):
    """
    Test_restaurant_break is start at 9:30:00 and end at 10:00:00.
    In this test endpoint should return 400 because booking would overlap restaurant break.
    """
    client = APIClient()
    client.force_authenticate(user=test_user)

    body = {
        "restaurant": test_restaurant.id,
        "guests": 4,
        "date": next_monday(),
        "start_time": "09:30:00",  # <-- At the same time when test_restaurant_break
    }
    response = client.post("/api/bookings/", body)
    assert response.status_code == 400
    assert response.data["error"] == "At provided time the restaurant has break"


def test_BookingViewSet_post_not_available_tables(test_user, test_restaurant, test_available_rule):
    """
    In this test at provided date restaurant does not have any available tables on provided amount of people.
    """
    client = APIClient()
    client.force_authenticate(user=test_user)
    body = {
        "restaurant": test_restaurant.id,
        "guests": 4,
        "date": next_monday(),
        "start_time": "16:30:00",
    }
    response = client.post("/api/bookings/", body)
    assert response.status_code == 400
    assert response.data["error"] == "No free tables available at provided time and date"


def test_BookingViewSet_post_requires_authentication():
    client = APIClient()
    response = client.post("/api/bookings/", {})
    assert response.status_code == 401
