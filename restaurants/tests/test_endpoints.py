from datetime import date, datetime, time, timedelta

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from booking_system.models import Booking
from restaurants.models import CuisineType, Restaurant, RestaurantBan
from user_reviews.models import Review


def next_monday():
    """
    Returns date of the next Monday.
    Test_available_rule in our test_restaurant in set on monday so in fild date we will use this function
    """
    today = date.today()
    days_until_next_monday = (6 - today.weekday()) + 1
    return today + timedelta(days=days_until_next_monday)


# Test for api/restaurants/all_cuisine_type/
@pytest.mark.django_db
def test_AllCuisinesTypeView(test_user):
    """
    In this test we create 2 example CuisineType models, and check whether
    our endpoint show us them correctly.
    """

    CuisineType.objects.create(
        name="test_cuisine_type_1",
    )
    CuisineType.objects.create(
        name="test_cuisine_type_2",
    )

    client = APIClient()
    client.force_authenticate(test_user)

    response = client.get("/api/restaurants/all_cuisine_type/")
    assert response.status_code == 200
    assert response.data["message"] == "All allowed cuisines types"
    # Check if in response we have exactly 2 CuisineType
    assert len(response.data["cuisine_types"]) == 2


def test_AllCuisinesTypeView_requires_authentication():
    client = APIClient()
    response = client.get("/api/restaurants/all_cuisine_type/")
    assert response.status_code == 401


# Test for api/restaurants/


# Get method
def test_RestaurantViewSet_get(test_user, test_cuisine_type):
    """
    In this test we create 2 example Restaurant models, and check whether
    endpoint show us them correctly.
    """
    Restaurant.objects.create(
        name="test_restaurant_1",
        owner=test_user,
        cuisine_type=test_cuisine_type,
        address="test_address_1",
        city="test_city_1",
    )

    Restaurant.objects.create(
        name="test_restaurant_2",
        owner=test_user,
        cuisine_type=test_cuisine_type,
        address="test_address_2",
        city="test_city_2",
    )

    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get("/api/restaurants/?page=1")
    assert response.status_code == 200
    assert len(response.data["results"]) == 2


def test_RestaurantViewSet_get_returns_average_rating(test_user, test_user_1, test_restaurant):
    """
    In this test we create 2 reviews of test_restaurant and check whether our endpoint
    show us average rating correct.

    The first review has 8 rating and the second has 7 so our average rating should be 7.5
    """
    # First review
    Review.objects.create(
        restaurant=test_restaurant,
        user=test_user,
        rating=8,
    )
    # Second review
    Review.objects.create(
        restaurant=test_restaurant,
        user=test_user_1,
        rating=7,
    )
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get("/api/restaurants/?page=1")
    assert response.status_code == 200
    restaurant = response.data["results"][0]
    assert restaurant["average_review_rating"] == 7.5


def test_restaurant_average_rating_after_new_review(test_user_2, test_restaurant, test_review_1, test_review_2):
    """
    When someone add, update or delete review of the restaurant average_rating is changed so cache
    that stores data about all restaurants should be cleaned.
    """
    client = APIClient()
    client.force_authenticate(test_user_2)
    # Firs two reviews test_review_1 and test_review_2 avg = 7.5
    response = client.get(f"/api/restaurants/{test_restaurant.id}/")
    assert response.data["average_review_rating"] == 7.5

    body = {"restaurant": test_restaurant.id, "rating": 6}
    # Create new review this should cleand cache
    client.post("/api/user_reviews/", body)
    # New avg = 7
    response = client.get(f"/api/restaurants/{test_restaurant.id}/")
    assert response.data["average_review_rating"] == 7


def test_RestaurantViewSet_get_filter_by_city(test_user_1, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_user_1)
    response = client.get(f"/api/restaurants/?city={test_restaurant.city}")
    assert response.status_code == 200


def test_RestaurantViewSet_get_requires_authentication():
    client = APIClient()
    response = client.get("/api/restaurants/")
    assert response.status_code == 401


# retrieve method
def test_RestaurantViewSet_retrieve(
    test_user, test_restaurant, test_available_rule, test_restaurant_table, test_restaurant_break
):
    """
    This test check whether in retrieve method endpoint correctly return additionally information about the restaurant.
    Such as full_address, available_rules or all allowed menus and more
    """
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get(f"/api/restaurants/{test_restaurant.id}/")
    assert response.status_code == 200

    data = response.data
    assert data["full_address"] == test_restaurant.full_address
    # restaurant available rules
    assert data["available_rules"][0]["opening_time"] == test_available_rule.opening_time
    assert data["available_rules"][0]["closing_time"] == test_available_rule.closing_time
    assert data["available_rules"][0]["day_of_week"] == test_available_rule.day_of_week
    # restaurant tables
    assert data["restaurant_tables"][0]["table_number"] == test_restaurant_table.table_number
    assert data["restaurant_tables"][0]["seats"] == test_restaurant_table.seats
    # restaurant breaks
    assert data["restaurant_breaks"][0]["start"] == test_restaurant_break.start
    assert data["restaurant_breaks"][0]["end"] == test_restaurant_break.end
    assert data["restaurant_breaks"][0]["day_of_week"] == test_restaurant_break.day_of_week


def test_RestaurantViewSet_get_details_invalid_id(test_user):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get(f"/api/restaurants/{404}/")
    assert response.status_code == 404


def test_RestaurantViewSet_get_details_authentication(test_restaurant):
    client = APIClient()
    response = client.get(f"/api/restaurants/{test_restaurant.id}/")
    assert response.status_code == 401


# Post method
def test_RestaurantViewSet_post(test_user, test_cuisine_type):
    """
    Checks if this endpoint correctly creates a new Restaurant
    """
    client = APIClient()
    client.force_authenticate(test_user)

    body = {
        "name": "test_restaurant_1",
        "cuisine_type": f"{test_cuisine_type.id}",
        "address": "test_address",
        "city": "test_city",
    }

    response = client.post("/api/restaurants/", body)
    assert response.status_code == 201

    assert Restaurant.objects.filter(name=body["name"]).exists()


@pytest.mark.parametrize(
    "payload, excepted_status",
    [
        # Missing name
        ({"name": "", "cuisine_type": 1, "address": "test_address", "city": "test_city"}, 400),
        # Missing cuisine_type
        ({"name": "test_restaurant_1", "cuisine_type": "", "address": "test_address", "city": "test_city"}, 400),
        # Missing address
        ({"name": "test_restaurant_1", "cuisine_type": 1, "address": "", "city": "test_city"}, 400),
        # Missing city
        ({"name": "test_restaurant_1", "cuisine_type": 1, "address": "test_address", "city": ""}, 400),
        # Provided name already exist
        ({"name": "test_restaurant", "cuisine_type": 1, "address": "test_address", "city": "test_city"}, 400),
    ],
)
def test_RestaurantViewSet_post_invalid_data(payload, excepted_status, test_user, test_restaurant, test_cuisine_type):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.post("/api/restaurants/", payload)
    assert response.status_code == excepted_status


def test_RestaurantViewSet_requires_authentication():
    client = APIClient()
    response = client.post("/api/restaurants/")
    assert response.status_code == 401


# Put method
def test_RestaurantViewSet_put_owner(test_owner, test_restaurant, test_cuisine_type):
    """
    Only owner or member with manager role have access to this endpoint
    """

    client = APIClient()
    client.force_authenticate(test_owner)

    body = {
        "name": "changed_name",
        "cuisine_type": f"{test_cuisine_type.id}",
        "address": "changed_address",
        "city": "changed_city",
    }

    response = client.put(f"/api/restaurants/{test_restaurant.id}/", body)
    test_restaurant.refresh_from_db()
    assert response.status_code == 200

    # Checks whether data has been changed correctly
    assert test_restaurant.name == body["name"]
    assert test_restaurant.address == body["address"]
    assert test_restaurant.city == body["city"]


def test_RestaurantViewSet_put_manager(test_membership_manager, test_restaurant, test_cuisine_type_2):
    """
    Only owner or member with manager role have access to this endpoint
    """
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)

    body = {
        "name": "changed_name",
        "cuisine_type": f"{test_cuisine_type_2.id}",
        "address": "changed_address",
        "city": "changed_city",
    }
    response = client.put(f"/api/restaurants/{test_restaurant.id}/", body)
    assert response.status_code == 200


def test_RestaurantViewSet_put_staff(test_membership_staff, test_restaurant, test_cuisine_type_2):
    """
    Member with staff role does not have access to this endpoint
    """
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)

    response = client.put(f"/api/restaurants/{test_restaurant.id}/", {})
    assert response.status_code == 403


def test_RestaurantViewSet_put_not_owner_or_manager(test_user_2, test_restaurant):
    """
    Normal user does not have access to this endpoint
    """
    client = APIClient()
    client.force_authenticate(test_user_2)

    response = client.put(f"/api/restaurants/{test_restaurant.id}/", {})
    assert response.status_code == 403


@pytest.mark.parametrize(
    "payload, excepted_status",
    [
        # Missing name
        ({"name": "", "cuisine_type": 1, "address": "test_address", "city": "test_city"}, 400),
        # Missing cuisine_type
        ({"name": "test_restaurant", "cuisine_type": "", "address": "test_address", "city": "test_city"}, 400),
        # Missing address
        ({"name": "test_restaurant", "cuisine_type": 1, "address": "", "city": "test_city"}, 400),
        # Missing city
        ({"name": "test_restaurant", "cuisine_type": 1, "address": "test_address", "city": ""}, 400),
        # Provided cuisine_type not exist
        ({"name": "test_restaurant", "cuisine_type": 3, "address": "test_address", "city": "test_city"}, 400),
    ],
)
def test_RestaurantViewSet_put_invalid_data(payload, excepted_status, test_owner, test_cuisine_type, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.put(f"/api/restaurants/{test_restaurant.id}/", payload)
    assert response.status_code == excepted_status


def test_RestaurantViewSet_put_requires_authentication():
    client = APIClient()
    response = client.put("/api/restaurants/")
    assert response.status_code == 401


# Patch method
def test_RestaurantViewSet_patch_owner(test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)

    body = {
        "name": "changed_name",
    }
    response = client.patch(f"/api/restaurants/{test_restaurant.id}/", body)
    test_restaurant.refresh_from_db()
    assert response.status_code == 200
    assert test_restaurant.name == body["name"]


def test_RestaurantViewSet_patch_manager(test_membership_manager, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    body = {
        "name": "changed_name",
    }
    response = client.patch(f"/api/restaurants/{test_restaurant.id}/", body)
    test_restaurant.refresh_from_db()
    assert response.status_code == 200
    assert test_restaurant.name == body["name"]


def test_RestaurantViewSet_patch_staff(test_membership_staff, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    response = client.patch(f"/api/restaurants/{test_restaurant.id}/", {})
    assert response.status_code == 403


def test_RestaurantViewSet_patch_not_owner_or_manager(test_user_2, test_restaurant):
    """
    Only the owner of provided restaurant has access to this action
    """
    client = APIClient()
    client.force_authenticate(test_user_2)
    response = client.patch(f"/api/restaurants/{test_restaurant.id}/", {})
    assert response.status_code == 403


def test_RestaurantViewSet_patch_requires_authentication():
    client = APIClient()
    response = client.put("/api/restaurants/")
    assert response.status_code == 401


# Delete method
"""
Only owner is allowed to delete his own restaurant 
"""


def test_RestaurantViewSet_delete_owner(test_owner, test_restaurant):

    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.delete(f"/api/restaurants/{test_restaurant.id}/")
    assert response.status_code == 204
    assert not Restaurant.objects.filter(id=test_restaurant.id).exists()


def test_RestaurantViewSet_delete_manager(test_membership_manager, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    response = client.delete(f"/api/restaurants/{test_restaurant.id}/")
    assert response.status_code == 403


def test_RestaurantViewSet_delete_staff(test_membership_staff, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    response = client.delete(f"/api/restaurants/{test_restaurant.id}/")
    assert response.status_code == 403


def test_RestaurantViewSet_delete_not_owner(test_user_2, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_user_2)
    response = client.delete(f"/api/restaurants/{test_restaurant.id}/")
    assert response.status_code == 403


def test_RestaurantViewSet_delete_requires_authentication():
    client = APIClient()
    response = client.delete("/api/restaurants/")
    assert response.status_code == 401


# Test for api/restaurants/id/reviews/


def test_get_reviews(test_restaurant, test_user, test_review_1, test_review_2):
    """
    In this test we create 2 reviews of test_restaurant and check whether our endpoint
    show us them correctly.
    """
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get(f"/api/restaurants/{test_restaurant.id}/reviews/")
    assert response.status_code == 200
    assert len(response.data["results"]) == 2


def test_get_reviews_cache_invalidation(test_restaurant, test_user, test_user_2, test_review_1, test_review_2):
    """
    When someone add, destroy or update a review of the restaurant cache should be cleaned so endpoint
    should return updated lists of reviews
    """
    client = APIClient()
    client.force_authenticate(test_user)
    # Firs request save 2 reviews in cache test_review_1 and test_review_2
    response = client.get(f"/api/restaurants/{test_restaurant.id}/reviews/")
    assert response.data["count"] == 2
    # Create new review that should clean cache
    client.force_authenticate(test_user_2)
    body = {"restaurant": test_restaurant.id, "rating": 5}
    client.post("/api/user_reviews/", body)

    # Send second request should return 3 reviews not 2 from cache
    response = client.get(f"/api/restaurants/{test_restaurant.id}/reviews/")
    assert response.data["count"] == 3


# Tests /api/restaurants/id/available_hours/
def test_available_hours(test_restaurant, test_available_rule, test_user, test_restaurant_table):
    """
    The test restaurant has no existing bookings for the provided date.
    According to test_available_rule, the restaurant is open on Mondays from 08:00 to 22:00.

    The restaurant reservation interval is set to 30 minutes, so available slots
    should be generated every 2 hours:
    08:00, 08:30, 09:00, 09:30, etc.

    The last available slot is 20:30 instead of 22:00 because the reservation duration
    is 90 minutes. A user cannot create a reservation if it would exceed the restaurant
    closing time.
    """
    client = APIClient()
    client.force_authenticate(test_user)

    # Monday because test_available_rule is configured for Mondays
    test_date = next_monday().strftime("%Y-%m-%d")

    response = client.get(
        f"/api/restaurants/{test_restaurant.id}/available_hours/?date={test_date}&guests={test_restaurant_table.seats}"
    )
    assert response.status_code == 200
    assert response.data["date"] == test_date

    # Check the first two available slots and the last available slot
    assert response.data["all_available_hours"][0] == "08:00"
    assert response.data["all_available_hours"][1] == "08:30"
    assert response.data["all_available_hours"][-1] == "20:30"
    assert len(response.data["all_available_hours"]) == 26


def test_available_hours_excludes_booked_slot(test_restaurant, test_available_rule, test_user, test_restaurant_table):
    """
    The rules are the same as in test above but this time we create 1 booking object at provided date
    with start_time at 8:00 so now the first available time slot should be 09:30 (only when the created booking will end)
    and our all_available_hours should be less by 3 time slots than in test above because created booking will run from 8:00 to 9:30
    because reservation_duration_minutes = 90 minutes in the restaurant.
    """
    client = APIClient()
    client.force_authenticate(test_user)
    # Monday because test_available_rule is configured for Mondays
    test_date = next_monday().strftime("%Y-%m-%d")
    Booking.objects.create(
        user=test_user,
        restaurant=test_restaurant,
        table=test_restaurant_table,
        date=datetime.strptime(test_date, "%Y-%m-%d").date(),
        start_time=time(8, 0, 0),
    )

    response = client.get(
        f"/api/restaurants/{test_restaurant.id}/available_hours/?date={test_date}&guests={test_restaurant_table.seats}"
    )

    assert response.status_code == 200
    assert response.data["date"] == test_date

    # Now first should be 10:00 not 8:00
    assert response.data["all_available_hours"][0] == "09:30"
    assert response.data["all_available_hours"][1] == "10:00"
    assert response.data["all_available_hours"][-1] == "20:30"

    assert len(response.data["all_available_hours"]) == 23


# Tests /api/restaurants/id/all_bookings/


def test_all_bookings_restaurant_owner(test_restaurant, test_owner, test_restaurant_table, test_user):
    """
    In this test we create 2 booking objects and check if endpoint correctly show them to owner of the restaurant.
    The first should be booking_2 because we sorted bookings by start_time
    """

    booking_1 = Booking.objects.create(
        user=test_user,
        restaurant=test_restaurant,
        table=test_restaurant_table,
        date=next_monday(),
        start_time=time(15, 0, 0),
        status=Booking.Status.CONFIRMED,
    )
    booking_2 = Booking.objects.create(
        user=test_user,
        restaurant=test_restaurant,
        table=test_restaurant_table,
        date=next_monday(),
        start_time=time(10, 0, 0),
        status=Booking.Status.CONFIRMED,
    )
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get(
        f"/api/restaurants/{test_restaurant.id}/all_bookings/?date={next_monday().strftime('%Y-%m-%d')}"
    )
    assert response.status_code == 200
    assert len(response.data["all_bookings"]) == 2
    # booking_2 should be first because its start_time is 10:00
    assert response.data["all_bookings"][0]["id"] == booking_2.id

    # Second should be booking_1
    assert response.data["all_bookings"][1]["id"] == booking_1.id


@pytest.mark.parametrize(
    "user_status, expected_status",
    [
        ("unauthorized_user", status.HTTP_401_UNAUTHORIZED),
        ("normal_user", status.HTTP_403_FORBIDDEN),
        ("staff", status.HTTP_200_OK),
        ("manager", status.HTTP_200_OK),
        ("owner", status.HTTP_200_OK),
    ],
)
def test_all_bookings_permissions(
    user_status,
    expected_status,
    test_user_3,
    test_owner,
    test_membership_manager,
    test_membership_staff,
    test_restaurant,
):
    """
    Only members or owner of provided restaurant are allowed to see all bookings per day
    """
    client = APIClient()
    if user_status == "unauthorized_user":
        client.force_authenticate()
    if user_status == "normal_user":
        client.force_authenticate(test_user_3)
    if user_status == "staff":
        client.force_authenticate(test_membership_staff.user)
    if user_status == "manager":
        client.force_authenticate(test_membership_manager.user)
    if user_status == "owner":
        client.force_authenticate(test_owner)

    response = client.get(f"/api/restaurants/{test_restaurant.id}/all_bookings/")
    assert response.status_code == expected_status


def test_all_bookings_bookings_with_wrong_status(test_restaurant, test_owner, test_restaurant_table, test_user):
    """
    Our endpoint returns only bookings with status confirmed, completed and no show.In this create we create
    bookings with different status and expect that endpoint will not show us them
    """
    client = APIClient()
    client.force_authenticate(test_owner)
    Booking.objects.create(
        user=test_user,
        restaurant=test_restaurant,
        table=test_restaurant_table,
        date=next_monday(),
        start_time=time(10, 0, 0),
        status=Booking.Status.PENDING,
    )

    Booking.objects.create(
        user=test_user,
        restaurant=test_restaurant,
        table=test_restaurant_table,
        date=next_monday(),
        start_time=time(15, 0, 0),
        status=Booking.Status.CANCELLED,
    )
    response = client.get(
        f"/api/restaurants/{test_restaurant.id}/all_bookings/?date={next_monday().strftime('%Y-%m-%d')}"
    )
    assert response.status_code == status.HTTP_200_OK
    # Endpoint shouldn't return those 2 bookings above because they have wrong status
    assert len(response.data["all_bookings"]) == 0


def test_all_bookings_invalid_date(test_restaurant, test_owner):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get(f"/api/restaurants/{test_restaurant.id}/all_bookings/?date=wrong-format")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Invalid date format"


def test_all_bookings_restaurant_not_found(test_owner):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get("/api/restaurants/not_exist_id/")
    assert response.status_code == 404


# Tests /api/restaurants/id/ban_user/
@pytest.mark.parametrize(
    "user_status, expected_status",
    [
        ("unauthorized_user", status.HTTP_401_UNAUTHORIZED),
        ("normal_user", status.HTTP_403_FORBIDDEN),
        ("staff", status.HTTP_403_FORBIDDEN),
        ("manager", status.HTTP_201_CREATED),
        ("owner", status.HTTP_201_CREATED),
    ],
)
def test_ban_user_permissions(
    user_status,
    expected_status,
    test_user_3,
    test_membership_staff,
    test_membership_manager,
    test_owner,
    test_restaurant,
):
    """
    Only manager or owner of provided restaurant are allowed to ban users
    """
    client = APIClient()
    if user_status == "unauthorized_user":
        client.force_authenticate()
    if user_status == "normal_user":
        client.force_authenticate(test_user_3)
    if user_status == "staff":
        client.force_authenticate(test_membership_staff.user)
    if user_status == "manager":
        client.force_authenticate(test_membership_manager.user)
    if user_status == "owner":
        client.force_authenticate(test_owner)

    body = {
        "email": f"{test_user_3.email}",
        "description": "test description",
    }
    response = client.post(f"/api/restaurants/{test_restaurant.id}/ban_user/", body)
    assert response.status_code == expected_status
    if expected_status == status.HTTP_201_CREATED:
        assert RestaurantBan.objects.filter(
            user=test_user_3, restaurant=test_restaurant, description=body["description"]
        ).exists()


def test_ban_user_not_exist_email(test_restaurant, test_owner):
    client = APIClient()
    client.force_authenticate(test_owner)

    body = {
        "email": "not_exist_email",
    }
    response = client.post(f"/api/restaurants/{test_restaurant.id}/ban_user/", body)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["error"] == "User with provided email does not exist"


def test_ban_user_missing_email(test_restaurant, test_owner):
    client = APIClient()
    client.force_authenticate(test_owner)
    body = {
        "email": "",
    }
    response = client.post(f"/api/restaurants/{test_restaurant.id}/ban_user/", body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Email is required"


def test_ban_user_not_exist_restaurant(test_owner, test_user_3):
    client = APIClient()
    client.force_authenticate(test_owner)
    body = {
        "email": f"{test_user_3.email}",
    }
    response = client.post("/api/restaurants/not_exist_id/ban_user/", body)
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Tests /api/restaurants/id/unban_user/?email=..
@pytest.mark.parametrize(
    "user_status, expected_status",
    [
        ("unauthorized_user", status.HTTP_401_UNAUTHORIZED),
        ("normal_user", status.HTTP_403_FORBIDDEN),
        ("staff", status.HTTP_403_FORBIDDEN),
        ("manager", status.HTTP_204_NO_CONTENT),
        ("owner", status.HTTP_204_NO_CONTENT),
    ],
)
def test_unban_user_permission(
    user_status,
    expected_status,
    test_user_3,
    test_membership_staff,
    test_membership_manager,
    test_owner,
    test_restaurant,
    test_ban_user,
    test_restaurant_ban,
):
    """
    In this test test_ban_user has been banned at test_restaurant and are attempting to unban them.
    Only manager or owner of provided restaurant are allowed to unban users
    """
    client = APIClient()
    if user_status == "unauthorized_user":
        client.force_authenticate()
    if user_status == "normal_user":
        client.force_authenticate(test_user_3)
    if user_status == "staff":
        client.force_authenticate(test_membership_staff.user)
    if user_status == "manager":
        client.force_authenticate(test_membership_manager.user)
    if user_status == "owner":
        client.force_authenticate(test_owner)

    response = client.delete(f"/api/restaurants/{test_restaurant.id}/unban_user/?email={test_ban_user.email}")
    assert response.status_code == expected_status
    if expected_status == status.HTTP_204_NO_CONTENT:
        assert not RestaurantBan.objects.filter(id=test_restaurant_ban.id).exists()


def test_unban_user_not_exist_restaurant(test_owner, test_restaurant_ban, test_ban_user):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.delete(f"/api/restaurants/not_exist_restaurant/unban_user/?email={test_ban_user.email}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_unban_user_not_exist_email(test_owner, test_restaurant_ban, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.delete(f"/api/restaurants/{test_restaurant.id}/unban_user/?email=not_exist_email")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["error"] == "User with provided email does not exist"


def test_unban_user_missing_email(test_restaurant, test_owner):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.delete(f"/api/restaurants/{test_restaurant.id}/unban_user/")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Email is required"


def test_unban_user_ban_not_exist(test_owner, test_restaurant, test_user_1):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.delete(f"/api/restaurants/{test_restaurant.id}/unban_user/?email={test_user_1.email}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["error"] == "Provided user does not have ban in the restaurant"


# Tests /api/restaurants/id/list_bans/
@pytest.mark.parametrize(
    "user_status, expected_status",
    [
        ("unauthorized_user", status.HTTP_401_UNAUTHORIZED),
        ("normal_user", status.HTTP_403_FORBIDDEN),
        ("staff", status.HTTP_403_FORBIDDEN),
        ("manager", status.HTTP_200_OK),
        ("owner", status.HTTP_200_OK),
    ],
)
def test_list_bans_permission(
    user_status,
    expected_status,
    test_user_3,
    test_membership_staff,
    test_membership_manager,
    test_owner,
    test_restaurant,
    test_restaurant_ban,
):
    """
    Only manager or owner of provided restaurant are allowed check list all banned users.
    """
    client = APIClient()
    if user_status == "unauthorized_user":
        client.force_authenticate()
    if user_status == "normal_user":
        client.force_authenticate(test_user_3)
    if user_status == "staff":
        client.force_authenticate(test_membership_staff.user)
    if user_status == "manager":
        client.force_authenticate(test_membership_manager.user)
    if user_status == "owner":
        client.force_authenticate(test_owner)

    response = client.get(f"/api/restaurants/{test_restaurant.id}/list_bans/?page=1")
    print(response.data)
    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        # test_restaurant has only one ban "test_restaurant_ban"
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == test_restaurant_ban.id


@pytest.mark.parametrize(
    "ordering, expected_status",
    [
        ("created_at", status.HTTP_200_OK),
        ("-created_at", status.HTTP_200_OK),
        ("invalid_ordering", status.HTTP_400_BAD_REQUEST),
    ],
)
def test_list_bans_ordering(ordering, expected_status, test_owner, test_restaurant, test_user_1, test_user_2):
    """
    In this test we create 2 RestaurantBan in our Restaurant and check whether our endpoint
    show them in correct ordering.

    Action list_bans allowed manger or owner to provide filed ordering in query_params.
    Allowed ordering ("created_at", "-created_at") if user does not provide this filed default = "created_at"
    """
    client = APIClient()
    client.force_authenticate(test_owner)
    ban_1 = RestaurantBan.objects.create(
        user=test_user_1,
        restaurant=test_restaurant,
        description="test description 1",
    )
    ban_2 = RestaurantBan.objects.create(
        user=test_user_2,
        restaurant=test_restaurant,
        description="test description 2",
    )
    response = client.get(f"/api/restaurants/{test_restaurant.id}/list_bans/?ordering={ordering}")
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        # If field ordering = created_at ban_1 should be first because it has older date of creating
        if ordering == "created_at":
            assert response.data["results"][0]["id"] == ban_1.id
            assert response.data["results"][1]["id"] == ban_2.id
        # If field ordering = -created_at ban_2 should be first because it has earlier date of creating
        if ordering == "-created_at":
            assert response.data["results"][0]["id"] == ban_2.id
            assert response.data["results"][1]["id"] == ban_1.id


def test_list_bans_restaurant_not_exist(test_owner):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get("/api/restaurants/not_exist_restaurant/list_bans/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_bans_returns_404_for_invalid_page(test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get(f"/api/restaurants/{test_restaurant.id}/list_bans/?page=invalid_page")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Tests /api/restaurants/id/check_user/?email=..
@pytest.mark.parametrize(
    "user_status, expected_status",
    [
        ("unauthorized_user", status.HTTP_401_UNAUTHORIZED),
        ("normal_user", status.HTTP_403_FORBIDDEN),
        ("staff", status.HTTP_403_FORBIDDEN),
        ("manager", status.HTTP_200_OK),
        ("owner", status.HTTP_200_OK),
    ],
)
def test_check_user_permissions(
    user_status,
    expected_status,
    test_user_3,
    test_membership_staff,
    test_membership_manager,
    test_owner,
    test_restaurant,
):
    """
    In this test we ban test_user_3 and expect that endpoint display this ban only for owner and manager of
    the restaurant on which this user jas been banned.
    """
    client = APIClient()
    if user_status == "unauthorized_user":
        client.force_authenticate()
    if user_status == "normal_user":
        client.force_authenticate(test_user_3)
    if user_status == "staff":
        client.force_authenticate(test_membership_staff.user)
    if user_status == "manager":
        client.force_authenticate(test_membership_manager.user)
    if user_status == "owner":
        client.force_authenticate(test_owner)

    # Ban test_user_3
    test_ban = RestaurantBan.objects.create(
        user=test_user_3,
        restaurant=test_restaurant,
        description="test description",
    )
    response = client.get(f"/api/restaurants/{test_restaurant.id}/check_user/?email={test_user_3.email}")
    assert response.status_code == expected_status
    # Check all ban details
    if expected_status == status.HTTP_200_OK:
        assert response.data["id"] == test_ban.id
        assert response.data["user_email"] == test_ban.user.email
        assert response.data["restaurant_name"] == test_ban.restaurant.name


def test_check_user_missing_email(test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get(f"/api/restaurants/{test_restaurant.id}/check_user/")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Email is required"


def test_check_user_not_exist_restaurant(test_owner, test_user_3):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get(f"/api/restaurants/not_exist_restaurant/check_user/?email={test_user_3.email}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_check_user_not_exist_email(test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get(f"/api/restaurants/{test_restaurant.id}/check_user/?email=not_exist_email")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["error"] == "User with provided email does not exist"


def test_check_user_return_404_for_user_without_ban(test_owner, test_restaurant, test_user_3):
    """
    In this test test_user_3 does not have ban at the restaurant.
    So endpoint should return 404 because RestaurantBan object doesn't exist.
    """
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get(f"/api/restaurants/{test_restaurant.id}/check_user/?email={test_user_3.email}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["error"] == "Provided user does not have ban in the restaurant"
