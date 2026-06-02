from datetime import datetime, time, timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from available_rules.models import AvailableRule, RestaurantBreak, RestaurantException, RestaurantTable

# test for api/available_rules/


# Post method
def test_AvailableRuleViewSet_post_owner(test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)

    body = {
        "restaurant": test_restaurant.id,
        "day_of_week": 1,
        "opening_time": "8:00",
        "closing_time": "22:00",
    }

    response = client.post("/api/available_rules/", body)
    assert response.status_code == 201
    assert AvailableRule.objects.filter(restaurant=test_restaurant.id, day_of_week=body["day_of_week"]).exists()


def test_AvailableRuleViewSet_post_manager(test_membership_manager, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    body = {
        "restaurant": test_restaurant.id,
        "day_of_week": 1,
        "opening_time": "8:00",
        "closing_time": "22:00",
    }
    response = client.post("/api/available_rules/", body)
    assert response.status_code == 201
    assert AvailableRule.objects.filter(restaurant=test_restaurant.id, day_of_week=body["day_of_week"]).exists()


def test_AvailableRuleViewSet_post_staff(test_membership_staff, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    body = {
        "restaurant": test_restaurant.id,
        "day_of_week": 1,
        "opening_time": "8:00",
        "closing_time": "22:00",
    }
    response = client.post("/api/available_rules/", body)
    assert response.status_code == 403


def test_AvailableRuleViewSet_post_not_member_of_restaurant(test_user_1, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_user_1)
    body = {
        "restaurant": test_restaurant.id,
        "day_of_week": 1,
        "opening_time": "8:00",
        "closing_time": "22:00",
    }
    response = client.post("/api/available_rules/", body)
    assert response.status_code == 403


def test_AvailableRuleViewSet_post_requires_authentication():
    client = APIClient()
    response = client.post("/api/available_rules/")
    assert response.status_code == 401


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Missing restaurant
        ({"restaurant": "", "day_of_week": 1, "opening_time": "8:00", "closing_time": "22:00"}, 400),
        # Missing day_of_week
        ({"restaurant": 1, "day_of_week": "", "opening_time": "8:00", "closing_time": "22:00"}, 400),
        # Missing opening_time
        ({"restaurant": 1, "day_of_week": 1, "opening_time": "", "closing_time": "22:00"}, 400),
        # Missing closing_time
        ({"restaurant": 1, "day_of_week": 1, "opening_time": "8:00", "closing_time": ""}, 400),
        # Incorrect format opening_time or closing_time
        ({"restaurant": 1, "day_of_week": 1, "opening_time": "8:00", "closing_time": "incorrect"}, 400),
        # Closing time after opening_time
        ({"restaurant": 1, "day_of_week": 1, "opening_time": "8:00", "closing_time": "6:00"}, 400),
        # Incorrect day_of_week allowed 1-7 from Monday=1 to Sunday=7
        ({"restaurant": 1, "day_of_week": 8, "opening_time": "8:00", "closing_time": "22:00"}, 400),
        # Not exist restaurant returns 403
        ({"restaurant": 2, "day_of_week": 1, "opening_time": "8:00", "closing_time": "22:00"}, 403),
    ],
)
def test_AvailableRuleViewSet_post_invalid_date(payload, expected_status, test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.post("/api/available_rules/", payload)
    assert response.status_code == expected_status


def test_AvailableRuleViewSet_post_unique_day_of_week(test_owner, test_restaurant):
    """
    Each restaurant can have only one rule per of day so in this test we create
    one AvailableRule model with day_of_week = 1(Monday) and then we try to create
    another one with the same day_of_week.And we excepted that our endpoint will not allow us
    to do that
    """
    client = APIClient()
    client.force_authenticate(test_owner)

    AvailableRule.objects.create(
        restaurant=test_restaurant,
        day_of_week=1,
        opening_time="8:00",
        closing_time="22:00",
    )

    body = {
        "restaurant": test_restaurant.id,
        "day_of_week": 1,
        "opening_time": "8:00",
        "closing_time": "21:00",
    }

    response = client.post("/api/available_rules/", body)
    assert response.status_code == 400


# Get method
def test_AvailableRuleViewSet_get_owner(test_owner, test_restaurant):
    """
    Owner of the restaurant has access to this endpoint.
    """
    client = APIClient()
    client.force_authenticate(test_owner)

    available_rule = AvailableRule.objects.create(
        restaurant=test_restaurant,
        day_of_week=1,
        opening_time="8:00",
        closing_time="22:00",
    )

    response = client.get("/api/available_rules/")

    assert response.status_code == 200

    # Checks if date will be return correctly
    assert len(response.data) == 1

    assert response.data[0]["restaurant"] == available_rule.restaurant.id
    assert response.data[0]["day_of_week"] == available_rule.day_of_week


def test_AvailableRuleViewSet_get_manager(test_membership_manager, test_restaurant):
    """
    Member of this restaurant with "manager" role has access to this endpoint.
    """
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)

    available_rule = AvailableRule.objects.create(
        restaurant=test_restaurant,
        day_of_week=1,
        opening_time="8:00",
        closing_time="22:00",
    )
    response = client.get("/api/available_rules/")
    assert response.status_code == 200

    # Checks if date will be return correctly
    assert len(response.data) == 1

    assert response.data[0]["restaurant"] == available_rule.restaurant.id
    assert response.data[0]["day_of_week"] == available_rule.day_of_week


def test_AvailableRuleViewSet_get_staff(test_membership_staff, test_restaurant):
    """
    Member of this restaurant with "staff" role has access to this endpoint.
    """
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)

    available_rule = AvailableRule.objects.create(
        restaurant=test_restaurant,
        day_of_week=1,
        opening_time="8:00",
        closing_time="22:00",
    )
    response = client.get("/api/available_rules/")
    assert response.status_code == 200

    # Checks if date will be return correctly
    assert len(response.data) == 1

    assert response.data[0]["restaurant"] == available_rule.restaurant.id
    assert response.data[0]["day_of_week"] == available_rule.day_of_week


def test_AvailableRuleViewSet_get_not_owner_or_member(test_user_2, test_restaurant):
    """
    test_user_2 is not a member of test_restaurant so endpoint should return 200 but
    with empty list even though we create 1 available_rule model with this restaurant.
    For public data he can use GET /api/restaurants/{id}/
    """
    client = APIClient()
    client.force_authenticate(test_user_2)

    AvailableRule.objects.create(
        restaurant=test_restaurant,
        day_of_week=1,
        opening_time="8:00",
        closing_time="22:00",
    )

    response = client.get("/api/available_rules/")
    assert response.status_code == 200
    assert len(response.data) == 0


def test_AvailableRuleViewSet_get_requires_authentication():
    client = APIClient()
    response = client.get("/api/available_rules/")
    assert response.status_code == 401


def test_AvailableRuleViewSet_retrive_owner(test_owner, test_restaurant):
    available_rule = AvailableRule.objects.create(
        restaurant=test_restaurant,
        day_of_week=1,
        opening_time="8:00",
        closing_time="22:00",
    )
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get(f"/api/available_rules/{available_rule.id}/")
    assert response.status_code == 200


def test_AvailableRuleViewSet_retrive_manager(test_membership_manager, test_restaurant):
    available_rule = AvailableRule.objects.create(
        restaurant=test_restaurant,
        day_of_week=1,
        opening_time="8:00",
        closing_time="22:00",
    )
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    response = client.get(f"/api/available_rules/{available_rule.id}/")
    assert response.status_code == 200


def test_AvailableRuleViewSet_retrive_staff(test_membership_staff, test_restaurant):
    available_rule = AvailableRule.objects.create(
        restaurant=test_restaurant,
        day_of_week=1,
        opening_time="8:00",
        closing_time="22:00",
    )
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    response = client.get(f"/api/available_rules/{available_rule.id}/")
    assert response.status_code == 200


def test_AvailableRuleViewSet_retrive_returns_404_for_non_owner_or_member(test_user, test_owner, test_restaurant):
    """
    If user is not owner or member of provided restaurant, return 404.
    User even does not know that this restaurant exists.
    """
    available_rule = AvailableRule.objects.create(
        restaurant=test_restaurant,
        day_of_week=1,
        opening_time="8:00",
        closing_time="22:00",
    )
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get(f"/api/available_rules/{available_rule.id}/")
    assert response.status_code == 404


# Put method
def test_AvailableRuleViewSet_put_owner(test_owner, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_owner)

    body = {
        "restaurant": test_available_rule.restaurant.id,
        "day_of_week": 7,
        "opening_time": "12:00",
        "closing_time": "20:00",
    }
    response = client.put(f"/api/available_rules/{test_available_rule.id}/", body)
    test_available_rule.refresh_from_db()
    assert response.status_code == 200

    # Checks if our data in test_available_rule has been changed correctly
    assert test_available_rule.day_of_week == body["day_of_week"]
    assert test_available_rule.opening_time == time(12, 0)
    assert test_available_rule.closing_time == time(20, 0)


def test_AvailableRuleViewSet_put_manager(test_membership_manager, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)

    body = {
        "restaurant": test_available_rule.restaurant.id,
        "day_of_week": 7,
        "opening_time": "12:00",
        "closing_time": "20:00",
    }
    response = client.put(f"/api/available_rules/{test_available_rule.id}/", body)
    test_available_rule.refresh_from_db()
    assert response.status_code == 200

    # Checks if our data in test_available_rule has been changed correctly
    assert test_available_rule.day_of_week == body["day_of_week"]
    assert test_available_rule.opening_time == time(12, 0)
    assert test_available_rule.closing_time == time(20, 0)


def test_AvailableRuleViewSet_put_staff(test_membership_staff, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    response = client.put(f"/api/available_rules/{test_available_rule.id}/", {})
    assert response.status_code == 403


def test_AvailableRuleViewSet_put_not_owner_or_manager_return_404(test_user_2, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_user_2)
    response = client.put(f"/api/available_rules/{test_available_rule.id}/", {})
    assert response.status_code == 404


def test_AvailableRuleViewSet_put_requires_authentication():
    client = APIClient()
    response = client.put("/api/available_rules/", {})
    assert response.status_code == 401


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Missing restaurant
        ({"restaurant": "", "day_of_week": 1, "opening_time": "8:00", "closing_time": "22:00"}, 400),
        # Missing day_of_week
        ({"restaurant": 1, "day_of_week": "", "opening_time": "8:00", "closing_time": "22:00"}, 400),
        # Missing opening_time
        ({"restaurant": 1, "day_of_week": 1, "opening_time": "", "closing_time": "22:00"}, 400),
        # Missing closing_time
        ({"restaurant": 1, "day_of_week": 1, "opening_time": "8:00", "closing_time": ""}, 400),
        # Incorrect format opening_time or closing_time
        ({"restaurant": 1, "day_of_week": 1, "opening_time": "8:00", "closing_time": "incorrect"}, 400),
        # Closing time after opening_time
        ({"restaurant": 1, "day_of_week": 1, "opening_time": "8:00", "closing_time": "6:00"}, 400),
        # Incorrect day_of_week allowed 1-7 from Monday=1 to Sunday=7
        ({"restaurant": 1, "day_of_week": 8, "opening_time": "8:00", "closing_time": "22:00"}, 400),
        # Not exist restaurant
        ({"restaurant": 2, "day_of_week": 1, "opening_time": "8:00", "closing_time": "22:00"}, 400),
    ],
)
def test_AvailableRuleViewSet_put_invalid_date(
    payload, expected_status, test_owner, test_restaurant, test_available_rule
):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.put(f"/api/available_rules/{test_available_rule.id}/", payload)
    assert response.status_code == expected_status


def test_AvailableRuleViewSet_put_not_found(test_owner):
    client = APIClient()
    client.force_authenticate(test_owner)

    # User provided not exist available_rule
    response = client.put("/api/available_rules/not_exists/", {})
    assert response.status_code == 404


# Patch method


def test_AvailableRuleViewSet_patch_owner(test_owner, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_owner)
    body = {
        "day_of_week": 7,
    }

    response = client.patch(f"/api/available_rules/{test_available_rule.id}/", body)
    test_available_rule.refresh_from_db()
    assert response.status_code == 200
    assert test_available_rule.day_of_week == body["day_of_week"]


def test_AvailableRuleViewSet_patch_manager(test_membership_manager, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    body = {
        "day_of_week": 7,
    }

    response = client.patch(f"/api/available_rules/{test_available_rule.id}/", body)
    test_available_rule.refresh_from_db()
    assert response.status_code == 200
    assert test_available_rule.day_of_week == body["day_of_week"]


def test_AvailableRuleViewSet_patch_staff(test_membership_staff, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    response = client.patch(f"/api/available_rules/{test_available_rule.id}/", {})
    assert response.status_code == 403


def test_AvailableRuleViewSet_patch_return_404_for_not_owner_or_manager(test_user_2, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_user_2)
    response = client.patch(f"/api/available_rules/{test_available_rule.id}/", {})
    assert response.status_code == 404


def test_AvailableRuleViewSet_patch_requires_authentication():
    client = APIClient()
    response = client.patch("/api/available_rules/", {})
    assert response.status_code == 401


def test_AvailableRuleViewSet_patch_not_found(test_owner, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_owner)

    # User provided not exist available_rule
    response = client.patch("/api/available_rules/not_exists/", {})
    assert response.status_code == 404


# Delete Method
def test_AvailableRuleViewSet_delete_owner(test_owner, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.delete(f"/api/available_rules/{test_available_rule.id}/")
    assert response.status_code == 204
    assert not AvailableRule.objects.filter(id=test_available_rule.id).exists()


def test_AvailableRuleViewSet_delete_manager(test_membership_manager, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    response = client.delete(f"/api/available_rules/{test_available_rule.id}/")
    assert response.status_code == 204
    assert not AvailableRule.objects.filter(id=test_available_rule.id).exists()


def test_AvailableRuleViewSet_delete_staff(test_membership_staff, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    response = client.delete(f"/api/available_rules/{test_available_rule.id}/")
    assert response.status_code == 403


def test_AvailableRuleViewSet_delete_return_404_for_not_owner_or_manager(test_user_2, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_user_2)
    response = client.delete(f"/api/available_rules/{test_available_rule.id}/")
    assert response.status_code == 404


def test_AvailableRuleViewSet_delete_requires_authentication():
    client = APIClient()
    response = client.delete("/api/available_rules/")
    assert response.status_code == 401


def test_AvailableRuleViewSet_delete_not_found(test_owner, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_owner)

    # User provided not exist available_rule
    response = client.delete("/api/available_rules/not_exists/")
    assert response.status_code == 404


# test for api/available_rules/restaurant_table/


# Post method
def test_RestaurantTableViewSet_post_owner(test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)
    body = {
        "restaurant": test_restaurant.id,
        "table_number": 2,
        "seats": 4,
    }
    response = client.post("/api/available_rules/restaurant_table/", body)
    assert response.status_code == 201
    assert RestaurantTable.objects.filter(restaurant=body["restaurant"], table_number=body["table_number"]).exists()


def test_RestaurantTableViewSet_post_manager(test_membership_manager, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    body = {
        "restaurant": test_restaurant.id,
        "table_number": "A10",
        "seats": 3,
    }
    response = client.post("/api/available_rules/restaurant_table/", body)
    assert response.status_code == 201
    assert RestaurantTable.objects.filter(restaurant=body["restaurant"], table_number=body["table_number"]).exists()


def test_RestaurantTableViewSet_post_staff(test_membership_staff, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    body = {
        "restaurant": test_restaurant.id,
        "table_number": "A10",
        "seats": 3,
    }
    response = client.post("/api/available_rules/restaurant_table/", body)
    assert response.status_code == 403


def test_RestaurantTableViewSet_post_not_owner_or_manager(test_user_2, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_user_2)
    body = {
        "restaurant": test_restaurant.id,
        "table_number": "A10",
        "seats": 3,
    }
    response = client.post("/api/available_rules/restaurant_table/", body)
    assert response.status_code == 403


def test_RestaurantTableViewSet_post_requires_authentication():
    client = APIClient()
    response = client.post("/api/available_rules/restaurant_table/")
    assert response.status_code == 401


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Missing restaurant
        ({"restaurant": "", "table_number": "A1", "seats": 4}, 400),
        # Missing table_number
        ({"restaurant": 1, "table_number": "", "seats": 4}, 400),
        # Missing seats
        ({"restaurant": 1, "table_number": "A1", "seats": ""}, 400),
        # Restaurant not exist return 403
        ({"restaurant": 2, "table_number": "A1", "seats": 4}, 403),
        # table numer is too long max length = 10
        ({"restaurant": 1, "table_number": "12345678910", "seats": 4}, 400),
        # Seats are not number
        ({"restaurant": 1, "table_number": "A1", "seats": "not_number"}, 400),
        # Seats are smaller than 1
        ({"restaurant": 1, "table_number": "A1", "seats": 0}, 400),
    ],
)
def test_RestaurantTableViewSet_post_invalid_date(payload, expected_status, test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.post("/api/available_rules/restaurant_table/", payload)
    assert response.status_code == expected_status


def test_RestaurantTableViewSet_post_unique_table_number(test_owner, test_restaurant):
    """
    Filed table_number has to be unique in the restaurant section.
    In this test we create a restaurant_table with table_number = A1 in test_restaurant, and then we try
    creates another table with the same table_number in this restaurant.
    """
    client = APIClient()
    client.force_authenticate(test_owner)
    RestaurantTable.objects.create(
        restaurant=test_restaurant,
        table_number="A1",
        seats=4,
    )

    body = {
        "restaurant": test_restaurant.id,
        "table_number": "A1",
        "seats": 3,
    }
    response = client.post("/api/available_rules/restaurant_table/", body)
    assert response.status_code == 400


# Get method
def test_RestaurantTableViewSet_get_owner(test_owner, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get("/api/available_rules/restaurant_table/")
    assert response.status_code == 200
    assert len(response.data) == 1


def test_RestaurantTableViewSet_get_manager(test_membership_manager, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    response = client.get("/api/available_rules/restaurant_table/")
    assert response.status_code == 200
    assert len(response.data) == 1


def test_RestaurantTableViewSet_get_staff(test_membership_staff, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    response = client.get("/api/available_rules/restaurant_table/")
    assert response.status_code == 200
    assert len(response.data) == 1


def test_RestaurantTableViewSet_get_not_owner_or_manager(test_user_2, test_restaurant_table):
    """
    User that is not member or owner get empty list.
    For public data he can use GET /api/restaurants/{id}/
    """
    client = APIClient()
    client.force_authenticate(test_user_2)
    response = client.get("/api/available_rules/restaurant_table/")
    assert response.status_code == 200
    assert len(response.data) == 0


def test_RestaurantTableViewSet_get_requires_authentication():
    client = APIClient()
    response = client.get("/api/available_rules/restaurant_table/")
    assert response.status_code == 401


def test_RestaurantTableViewSet_get_not_exist_table(test_owner, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get("/api/available_rules/restaurant_table/not_exist_table/")
    assert response.status_code == 404


def test_RestaurantTableViewSet_retrive_owner(test_owner, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/")
    assert response.status_code == 200


def test_RestaurantTableViewSet_retrive_manager(test_membership_manager, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    response = client.get(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/")
    assert response.status_code == 200


def test_RestaurantTableViewSet_retrive_staff(test_membership_staff, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    response = client.get(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/")
    assert response.status_code == 200


def test_RestaurantTableViewSet_retrive_return_404_for_not_owner_or_mamber(test_user_2, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_user_2)
    response = client.get(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/")
    assert response.status_code == 404


# Put method
def test_RestaurantTableViewSet_put_owner(test_owner, test_restaurant_table):

    client = APIClient()
    client.force_authenticate(test_owner)
    body = {
        "restaurant": test_restaurant_table.restaurant.id,
        "table_number": "A11",
        "seats": 3,
    }
    response = client.put(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/", body)
    test_restaurant_table.refresh_from_db()
    assert response.status_code == 200
    assert test_restaurant_table.table_number == body["table_number"]
    assert test_restaurant_table.seats == body["seats"]


def test_RestaurantTableViewSet_put_manager(test_membership_manager, test_restaurant_table):

    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    body = {
        "restaurant": test_restaurant_table.restaurant.id,
        "table_number": "A11",
        "seats": 3,
    }
    response = client.put(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/", body)
    test_restaurant_table.refresh_from_db()
    assert response.status_code == 200
    assert test_restaurant_table.table_number == body["table_number"]
    assert test_restaurant_table.seats == body["seats"]


def test_RestaurantTableViewSet_put_staff(test_membership_staff, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    response = client.put(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/", {})
    assert response.status_code == 403


def test_RestaurantTableViewSet_put_return_404_for_not_owner_or_member(test_user_2, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_user_2)
    response = client.put(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/", {})
    assert response.status_code == 404


def test_RestaurantTableViewSet_put_requires_authentication():
    client = APIClient()
    response = client.put("/api/available_rules/restaurant_table/")
    assert response.status_code == 401


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Missing restaurant
        ({"restaurant": "", "table_number": "A1", "seats": 4}, 400),
        # Missing table_number
        ({"restaurant": 1, "table_number": "", "seats": 4}, 400),
        # Missing seats
        ({"restaurant": 1, "table_number": "A1", "seats": ""}, 400),
        # Restaurant not exist
        ({"restaurant": 2, "table_number": "A1", "seats": 4}, 400),
        # table numer is too long max length = 10
        ({"restaurant": 1, "table_number": "12345678910", "seats": 4}, 400),
        # Seats are not number
        ({"restaurant": 1, "table_number": "A1", "seats": "not_number"}, 400),
        # Seats are smaller than 1
        ({"restaurant": 1, "table_number": "A1", "seats": 0}, 400),
    ],
)
def test_RestaurantTableViewSet_put_invalid_date(payload, expected_status, test_owner, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.put(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/", payload)
    assert response.status_code == expected_status


def test_RestaurantTableViewSet_put_not_found(test_owner):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.put("/api/available_rules/restaurant_table/not_exist_table/")
    assert response.status_code == 404


# Patch method
def test_RestaurantTableViewSet_patch_owner(test_owner, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_owner)
    body = {"seats": 3}
    response = client.patch(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/", body)
    test_restaurant_table.refresh_from_db()
    assert response.status_code == 200
    assert test_restaurant_table.seats == body["seats"]


def test_RestaurantTableViewSet_patch_manager(test_membership_manager, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    body = {"seats": 3}
    response = client.patch(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/", body)
    test_restaurant_table.refresh_from_db()
    assert response.status_code == 200
    assert test_restaurant_table.seats == body["seats"]


def test_RestaurantTableViewSet_patch_staff(test_membership_staff, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    response = client.put(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/", {})
    assert response.status_code == 403


def test_RestaurantTableViewSet_patch_return_404_for_not_owner_or_member(test_user_2, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_user_2)
    response = client.put(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/", {})
    assert response.status_code == 404


def test_RestaurantTableViewSet_patch_not_found(test_owner):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.patch("/api/available_rules/restaurant_table/not_exist_table/")
    assert response.status_code == 404


def test_RestaurantTableViewSet_patch_requires_authentication():
    client = APIClient()
    response = client.patch("/api/available_rules/restaurant_table/")
    assert response.status_code == 401


# Delete method
def test_RestaurantTableViewSet_delete_owner(test_owner, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.delete(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/")
    assert response.status_code == 204
    assert not RestaurantTable.objects.filter(id=test_restaurant_table.id).exists()


def test_RestaurantTableViewSet_delete_manager(test_membership_manager, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    response = client.delete(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/")
    assert response.status_code == 204
    assert not RestaurantTable.objects.filter(id=test_restaurant_table.id).exists()


def test_RestaurantTableViewSet_delete_staff(test_membership_staff, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    response = client.delete(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/")
    assert response.status_code == 403


def test_RestaurantTableViewSet_delete_return_404_for_not_owner_or_member(test_user_2, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_user_2)
    response = client.delete(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/")
    assert response.status_code == 404


def test_RestaurantTableViewSet_delete_requires_authentication():
    client = APIClient()
    response = client.get("/api/available_rules/restaurant_table/")
    assert response.status_code == 401


def test_RestaurantTableViewSet_delete_not_found(test_owner):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.delete("/api/available_rules/restaurant_table/not_found/")
    assert response.status_code == 404


# Tests for /api/available_rules/restaurant_break/


def test_RestaurantBreakViewSet_post(test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)

    body = {"restaurant": test_restaurant.id, "start": "10:00", "end": "10:25"}

    response = client.post("/api/available_rules/restaurant_break/", body)
    assert response.status_code == 201
    assert RestaurantBreak.objects.filter(restaurant=test_restaurant).exists()


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Missing restaurant
        ({"restaurant": "", "start": "10:00", "end": "10:25"}, 400),
        # Missing start
        ({"restaurant": 1, "start": "", "end": "10:25"}, 400),
        # Missing end
        ({"restaurant": 1, "start": "10:00", "end": ""}, 400),
        # Restaurant does not exist
        ({"restaurant": 2, "start": "10:00", "end": "10:25"}, 400),
        # Incorrect data format start or end
        ({"restaurant": 1, "start": "10:00", "end": "wrong_format"}, 400),
        # Start before end
        ({"restaurant": 1, "start": "10:00", "end": "9:59"}, 400),
    ],
)
def test_RestaurantBreakViewSet_post_invalid_data(payload, expected_status, test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.post("/api/available_rules/restaurant_break/", payload)
    assert response.status_code == expected_status


def test_RestaurantBreakViewSet_post_not_restaurant_owner(test_user, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_user)
    body = {"restaurant": test_restaurant.id, "start": "10:00", "end": "10:25"}
    response = client.post("/api/available_rules/restaurant_break/", body)
    assert response.status_code == 403


def test_RestaurantBreakViewSet_post_requires_authentication():
    client = APIClient()
    response = client.post("/api/available_rules/restaurant_break/")
    assert response.status_code == 401


# Get method
def test_RestaurantBreakViewSet_get(test_owner, test_restaurant_break):
    """
    Test_owner has only 1 restaurant_break model in his restaurant
    so our endpoint should return only 1 restaurant_break model
    """
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get("/api/available_rules/restaurant_break/")
    assert response.status_code == 200
    assert len(response.data) == 1


def test_RestaurantBreakViewSet_get_details(test_owner, test_restaurant_break):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get(f"/api/available_rules/restaurant_break/{test_restaurant_break.id}/")
    assert response.status_code == 200


def test_RestaurantBreakViewSet_get_returns_404_for_not_owner(test_user, test_restaurant_break):
    """
    Users should only see restaurant_break models that belong to them.
    The restaurant in test_restaurant_break belongs to test_owner, not test_user,
    so the endpoint should return 404.
    """

    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get(f"/api/available_rules/restaurant_break/{test_restaurant_break.id}/")
    assert response.status_code == 404


def test_RestaurantBreakViewSet_get_requires_authentication():
    client = APIClient()
    response = client.get("/api/available_rules/restaurant_break/")
    assert response.status_code == 401


# Put method
def test_RestaurantBreakViewSet_put(test_owner, test_restaurant_break):
    client = APIClient()
    client.force_authenticate(test_owner)
    body = {"restaurant": test_restaurant_break.restaurant.id, "start": "15:00", "end": "16:25"}
    response = client.put(f"/api/available_rules/restaurant_break/{test_restaurant_break.id}/", body)
    test_restaurant_break.refresh_from_db()
    assert response.status_code == 200

    # Checks if data in our restaurant_break has been changed
    assert test_restaurant_break.start == time(15, 0)
    assert test_restaurant_break.end == time(16, 25)


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Missing restaurant
        ({"restaurant": "", "start": "10:00", "end": "10:25"}, 400),
        # Missing start
        ({"restaurant": 1, "start": "", "end": "10:25"}, 400),
        # Missing end
        ({"restaurant": 1, "start": "10:00", "end": ""}, 400),
        # Restaurant does not exist
        ({"restaurant": 2, "start": "10:00", "end": "10:25"}, 400),
        # Incorrect data format start or end
        ({"restaurant": 1, "start": "10:00", "end": "wrong_format"}, 400),
        # Start before end
        ({"restaurant": 1, "start": "10:00", "end": "9:59"}, 400),
    ],
)
def test_RestaurantBreakViewSet_put_invalid_data(
    payload, expected_status, test_owner, test_restaurant, test_restaurant_break
):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.put(f"/api/available_rules/restaurant_break/{test_restaurant_break.id}/", payload)
    assert response.status_code == expected_status


def test_RestaurantBreakViewSet_put_returns_404_for_not_owner(test_user, test_restaurant_break):
    """
    test_user is not owner of restaurant in test_restaurant_break.
    Endpoint should return 404 for test_user.
    """
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.put(f"/api/available_rules/restaurant_break/{test_restaurant_break.id}/", {})
    assert response.status_code == 404


def test_RestaurantBreakViewSet_put_requires_authentication():
    client = APIClient()
    response = client.put("/api/available_rules/restaurant_break/")
    assert response.status_code == 401


# Patch method


def test_RestaurantBreakViewSet_patch(test_owner, test_restaurant_break):
    client = APIClient()
    client.force_authenticate(test_owner)
    body = {"start": "15:00", "end": "15:25"}
    response = client.patch(f"/api/available_rules/restaurant_break/{test_restaurant_break.id}/", body)
    test_restaurant_break.refresh_from_db()
    assert response.status_code == 200
    assert test_restaurant_break.start == time(15, 0)
    assert test_restaurant_break.end == time(15, 25)


def test_RestaurantBreakViewSet_patch_start_before_end(test_owner, test_restaurant_break):
    client = APIClient()
    client.force_authenticate(test_owner)
    body = {"start": "15:00", "end": "14:59"}
    response = client.patch(f"/api/available_rules/restaurant_break/{test_restaurant_break.id}/", body)
    assert response.status_code == 400


def test_RestaurantBreakViewSet_patch_returns_404_for_not_owner(test_user, test_restaurant_break):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.patch(f"/api/available_rules/restaurant_break/{test_restaurant_break.id}/", {})
    assert response.status_code == 404


def test_RestaurantBreakViewSet_patch_requires_authentication():
    client = APIClient()
    response = client.patch("/api/available_rules/restaurant_break/")
    assert response.status_code == 401


# Delete method
def test_RestaurantBreakViewSet_delete(test_owner, test_restaurant_break):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.delete(f"/api/available_rules/restaurant_break/{test_restaurant_break.id}/")
    assert response.status_code == 204
    assert not RestaurantBreak.objects.filter(id=test_restaurant_break.id).exists()


def test_RestaurantBreakViewSet_delete_returns_404_for_not_owner(test_user, test_restaurant_break):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.delete(f"/api/available_rules/restaurant_break/{test_restaurant_break.id}/")
    assert response.status_code == 404


def test_RestaurantBreakViewSet_delete_requires_authentication():
    client = APIClient()
    response = client.delete("/api/available_rules/restaurant_break/")
    assert response.status_code == 401


# Tests for /api/available_rules/restaurant_exception/


# Post method
def test_RestaurantExceptionViewSet_post_type_closed(test_owner, test_restaurant):
    """
    In this test we create a RestaurantException model with type = closed so fields
    opening_time and closing_time must be empty.
    """
    client = APIClient()
    client.force_authenticate(test_owner)
    tomorrow = (timezone.now() + timedelta(days=1)).date().isoformat()
    body = {
        "restaurant": test_restaurant.id,
        "date": tomorrow,
        "type": "closed",
    }
    response = client.post("/api/available_rules/restaurant_exception/", body)
    assert response.status_code == 201
    assert RestaurantException.objects.filter(restaurant=test_restaurant).exists()


def test_RestaurantExceptionViewSet_post_type_special_hours(test_owner, test_restaurant):
    """
    In this test we create a RestaurantException model with type = special_hours so fields
    opening_time and closing_time are required.
    """
    client = APIClient()
    client.force_authenticate(test_owner)
    tomorrow = (timezone.now() + timedelta(days=1)).date().isoformat()
    body = {
        "restaurant": test_restaurant.id,
        "date": tomorrow,
        "type": "special_hours",
        "opening_time": "8:00",
        "closing_time": "22:00",
    }
    response = client.post("/api/available_rules/restaurant_exception/", body)
    assert response.status_code == 201
    assert RestaurantException.objects.filter(restaurant=test_restaurant).exists()


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Missing restaurant
        ({"restaurant": "", "date": "3000-05-26", "type": "closed"}, 400),
        # Missing date
        ({"restaurant": 1, "date": "", "type": "closed"}, 400),
        # Missing type
        ({"restaurant": 1, "date": "3000-05-26", "type": ""}, 400),
        # Not exist restaurant
        ({"restaurant": 2, "date": "3000-05-26", "type": "closed"}, 400),
        # Wrong date formant
        ({"restaurant": 1, "date": "wrong_format", "type": "closed"}, 400),
        # Date is in the past (current data = 2026-05-26)
        ({"restaurant": 1, "date": "1996-05-26", "type": "closed"}, 400),
        # Wrong type allowed (closed, special_hours)
        ({"restaurant": 1, "date": "3000-05-26", "type": "wrong_type"}, 400),
        # Type = closed and fields opening_time and closing_time are not empty
        (
            {"restaurant": 1, "date": "3000-05-26", "type": "closed", "opening_time": "8:00", "closing_time": "22:00"},
            400,
        ),
        # Closing_time before opening_time
        (
            {
                "restaurant": 1,
                "date": "3000-05-26",
                "type": "special_hours",
                "opening_time": "22:00",
                "closing_time": "8:00",
            },
            400,
        ),
        # Type = special_hours and fields opening_time and closing_time are empty
        ({"restaurant": 1, "date": "3000-05-26", "type": "special_hours"}, 400),
    ],
)
def test_RestaurantExceptionViewSet_post_invalid_data(payload, expected_status, test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.post("/api/available_rules/restaurant_exception/", payload)
    assert response.status_code == expected_status


def test_RestaurantExceptionViewSet_post_not_restaurant_owner(test_user, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_user)
    body = {
        "restaurant": test_restaurant.id,
        "date": "3000-05-26",
        "type": "closed",
    }
    response = client.post("/api/available_rules/restaurant_exception/", body)
    assert response.status_code == 403


def test_RestaurantExceptionViewSet_post_requires_authentication():
    client = APIClient()
    response = client.post("/api/available_rules/restaurant_exception/")
    assert response.status_code == 401


# Get method
def test_RestaurantExceptionViewSet_get(test_owner, test_restaurant_exception):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get("/api/available_rules/restaurant_exception/")
    assert response.status_code == 200
    assert len(response.data) == 1


def test_RestaurantExceptionViewSet_get_details(test_owner, test_restaurant_exception):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get(f"/api/available_rules/restaurant_exception/{test_restaurant_exception.id}/")
    assert response.status_code == 200


def test_RestaurantExceptionViewSet_get_returns_404_for_not_owner(test_user, test_restaurant_exception):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get(f"/api/available_rules/restaurant_exception/{test_restaurant_exception.id}/")
    assert response.status_code == 404


def test_RestaurantExceptionViewSet_get_requires_authentication():
    client = APIClient()
    response = client.get("/api/available_rules/restaurant_exception/")
    assert response.status_code == 401


# Put method
def test_RestaurantExceptionViewSet_put(test_owner, test_restaurant_exception):
    client = APIClient()
    client.force_authenticate(test_owner)
    body = {
        "restaurant": test_restaurant_exception.restaurant.id,
        "date": "3001-05-26",
        "type": "closed",
    }

    response = client.put(f"/api/available_rules/restaurant_exception/{test_restaurant_exception.id}/", body)
    test_restaurant_exception.refresh_from_db()
    assert response.status_code == 200
    assert test_restaurant_exception.date == datetime.strptime(body["date"], "%Y-%m-%d").date()


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Missing restaurant
        ({"restaurant": "", "date": "3000-05-26", "type": "closed"}, 400),
        # Missing date
        ({"restaurant": 1, "date": "", "type": "closed"}, 400),
        # Missing type
        ({"restaurant": 1, "date": "3000-05-26", "type": ""}, 400),
        # Not exist restaurant
        ({"restaurant": 2, "date": "3000-05-26", "type": "closed"}, 400),
        # Wrong date formant
        ({"restaurant": 1, "date": "wrong_format", "type": "closed"}, 400),
        # Date is in the past (current data = 2026-05-26)
        ({"restaurant": 1, "date": "1996-05-26", "type": "closed"}, 400),
        # Wrong type allowed (closed, special_hours)
        ({"restaurant": 1, "date": "3000-05-26", "type": "wrong_type"}, 400),
        # Type = closed and fields opening_time and closing_time are not empty
        (
            {"restaurant": 1, "date": "3000-05-26", "type": "closed", "opening_time": "8:00", "closing_time": "22:00"},
            400,
        ),
        # Closing_time before opening_time
        (
            {
                "restaurant": 1,
                "date": "3000-05-26",
                "type": "special_hours",
                "opening_time": "22:00",
                "closing_time": "8:00",
            },
            400,
        ),
        # Type = special_hours and fields opening_time and closing_time are empty
        ({"restaurant": 1, "date": "3000-05-26", "type": "special_hours"}, 400),
    ],
)
def test_RestaurantExceptionViewSet_put_invalid_data(
    payload, expected_status, test_owner, test_restaurant, test_restaurant_exception
):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.put(f"/api/available_rules/restaurant_exception/{test_restaurant_exception.id}/", payload)
    assert response.status_code == expected_status


def test_RestaurantExceptionViewSet_put_returns_404_for_not_owner(test_user, test_restaurant_exception):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.put(f"/api/available_rules/restaurant_exception/{test_restaurant_exception.id}/", {})
    assert response.status_code == 404


def test_RestaurantExceptionViewSet_put_requires_authentication(test_restaurant_exception):
    client = APIClient()
    response = client.put(f"/api/available_rules/restaurant_exception/{test_restaurant_exception.id}/", {})
    assert response.status_code == 401


# Patch method
def test_RestaurantExceptionViewSet_patch(test_owner, test_restaurant_exception):
    client = APIClient()
    client.force_authenticate(test_owner)

    body = {
        "date": "3005-05-26",
    }
    response = client.patch(f"/api/available_rules/restaurant_exception/{test_restaurant_exception.id}/", body)
    test_restaurant_exception.refresh_from_db()
    assert response.status_code == 200
    assert test_restaurant_exception.date == datetime.strptime(body["date"], "%Y-%m-%d").date()


def test_RestaurantExceptionViewSet_patch_returns_404_for_not_owner(test_user, test_restaurant_exception):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.patch(f"/api/available_rules/restaurant_exception/{test_restaurant_exception.id}/", {})
    assert response.status_code == 404


def test_RestaurantExceptionViewSet_patch_requires_authentication(test_restaurant_exception):
    client = APIClient()
    response = client.patch(f"/api/available_rules/restaurant_exception/{test_restaurant_exception.id}/", {})
    assert response.status_code == 401


# Delete method
def test_RestaurantExceptionViewSet_delete(test_owner, test_restaurant_exception):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.delete(f"/api/available_rules/restaurant_exception/{test_restaurant_exception.id}/")
    assert response.status_code == 204
    assert not RestaurantException.objects.filter(id=test_restaurant_exception.id).exists()


def test_RestaurantExceptionViewSet_delete_returns_404_for_not_owner(test_user, test_restaurant_exception):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.delete(f"/api/available_rules/restaurant_exception/{test_restaurant_exception.id}/")
    assert response.status_code == 404


def test_RestaurantExceptionViewSet_delete_requires_authentication(test_restaurant_exception):
    client = APIClient()
    response = client.delete(f"/api/available_rules/restaurant_exception/{test_restaurant_exception.id}/")
    assert response.status_code == 401
