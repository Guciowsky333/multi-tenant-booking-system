import uuid
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


# Test /api/bookings/


# Post method
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


def test_BookingViewSet_post_start_time_not_aligned_to_interval(
    test_user, test_restaurant, test_available_rule, test_restaurant_table
):
    """
    Each restaurant have field "reservation_interval_minutes".In this test user try to create
    booking model with start_time that is not consistent with that filed.

    reservation_interval_minutes = 30 minutes
    restaurant opening_time = 08:00:00
    User set up start_time at 08:27:00 so endpoint should return 400
    """
    client = APIClient()
    client.force_authenticate(user=test_user)

    body = {
        "restaurant": test_restaurant.id,
        "guests": 4,
        "date": next_monday(),
        "start_time": "08:27:00",
    }

    response = client.post("/api/bookings/", body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == (
        f"Invalid start time. Bookings in this restaurant can only start every "
        f"{test_restaurant.reservation_interval_minutes} minutes from opening time."
    )


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


# Get method


def test_BookingViewSet_get(test_user, test_booking_1, test_booking_2):
    """
    Endpoint should return all user's bookings sorted by date.
    """

    client = APIClient()
    client.force_authenticate(user=test_user)
    response = client.get("/api/bookings/?page=1")
    assert response.status_code == status.HTTP_200_OK

    # test_booking_2 has earlier date so it should be first adn then test_booking_1 with older date
    assert response.data["results"][0]["id"] == test_booking_2.id
    assert response.data["results"][1]["id"] == test_booking_1.id


def test_BookingViewSet_get_requires_authentication():
    client = APIClient()
    response = client.get("/api/bookings/?page=1")
    assert response.status_code == 401


def test_BookingViewSet_get_details(test_user, test_booking_1):
    client = APIClient()
    client.force_authenticate(user=test_user)
    response = client.get(f"/api/bookings/{test_booking_1.id}/")
    assert response.status_code == status.HTTP_200_OK
    # checking all data
    booking = response.data
    assert booking["id"] == test_booking_1.id
    assert booking["restaurant_name"] == test_booking_1.restaurant.name
    assert booking["table_number"] == test_booking_1.table.table_number
    assert booking["table_seats"] == test_booking_1.table.seats
    assert booking["user_email"] == test_user.email
    assert booking["status"] == test_booking_1.status
    assert booking["date"] == str(test_booking_1.date)
    assert booking["start_time"] == str(test_booking_1.start_time)


def test_BookingViewSet_get_details_returns_404_for_not_owner(test_user_2, test_booking_1):
    """
    In this test test_user_2 is not the owner of test_booking_1 so endpoint should return 404.
    """
    client = APIClient()
    client.force_authenticate(user=test_user_2)
    response = client.get(f"/api/bookings/{test_booking_1.id}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_BookingViewSet_get_details_requires_authentication(test_booking_1):
    client = APIClient()
    response = client.get(f"/api/bookings/{test_booking_1.id}/")
    assert response.status_code == 401


# action method /api/bookings/status_confirmed/?token=xxx
def test_BookingViewSet_change_status_confirmed(test_booking_1):
    client = APIClient()
    response = client.get(f"/api/bookings/status_confirmed/?token={test_booking_1.confirmation_token}")

    test_booking_1.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert test_booking_1.status == "confirmed"


def test_BookingViewSet_change_status_confirmed_invalid_token(test_booking_1):
    client = APIClient()
    response = client.get("/api/bookings/status_confirmed/?token=invalid_token")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Invalid token"


def test_BookingViewSet_change_status_confirmed_not_found_booking(test_booking_1):
    fake_token = uuid.uuid4()
    client = APIClient()
    response = client.get(f"/api/bookings/status_confirmed/?token={fake_token}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["error"] == "Booking not found"


@pytest.mark.parametrize(
    "booking_status, message",
    [
        ("confirmed", "Booking is already confirmed"),
        ("cancelled", "Booking has been cancelled you can not change its status"),
        ("completed", "Booking has been already completed"),
    ],
)
def test_BookingViewSet_change_status_confirmed_status_different_than_pending(booking_status, message, test_booking_1):
    """
    To change status of booking on confirmed it must have status pending.
    """
    client = APIClient()
    test_booking_1.status = booking_status
    test_booking_1.save()
    response = client.get(f"/api/bookings/status_confirmed/?token={test_booking_1.confirmation_token}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == message
