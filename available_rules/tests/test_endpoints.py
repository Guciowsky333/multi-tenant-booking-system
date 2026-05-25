from datetime import time

import pytest
from rest_framework.test import APIClient

from available_rules.models import AvailableRule, RestaurantTable

# test for api/available_rules/


# Post method
def test_AvailableRuleViewSet_post(test_owner, test_restaurant):
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
    assert AvailableRule.objects.filter(restaurant=test_restaurant.id, day_of_week=1).exists()


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


def test_AvailableRuleViewSet_post_not_owner(test_user, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_user)
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


# Get method
def test_AvailableRuleViewSet_get(test_owner, test_restaurant):
    """
    In this test we create 2 AvailableRule models and check whether
    endpoint show us them correctly
    """
    client = APIClient()
    client.force_authenticate(test_owner)

    available_rule_1 = AvailableRule.objects.create(
        restaurant=test_restaurant,
        day_of_week=1,
        opening_time="8:00",
        closing_time="22:00",
    )
    available_rule_2 = AvailableRule.objects.create(
        restaurant=test_restaurant,
        day_of_week=7,
        opening_time="10:00",
        closing_time="20:00",
    )

    response = client.get("/api/available_rules/")

    assert response.status_code == 200
    assert len(response.data) == 2

    assert response.data[0]["restaurant"] == available_rule_1.restaurant.id
    assert response.data[0]["day_of_week"] == available_rule_1.day_of_week

    assert response.data[1]["restaurant"] == available_rule_2.restaurant.id
    assert response.data[1]["day_of_week"] == available_rule_2.day_of_week


def test_AvailableRuleViewSet_get_requires_authentication():
    client = APIClient()
    response = client.get("/api/available_rules/")
    assert response.status_code == 401


def test_AvailableRuleViewSet_get_returns_404_for_non_owner(test_user, test_owner, test_restaurant):
    """
    In this test we create 1 AvailableRule model with restaurant that belong to test_owner
    and then check whether different user has access to it
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
def test_AvailableRuleViewSet_put(test_owner, test_available_rule):
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


def test_AvailableRuleViewSet_put_returns_404_for_non_owner(test_user, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.put(f"/api/available_rules/{test_available_rule.id}/", {})
    assert response.status_code == 404


def test_AvailableRuleViewSet_put_requires_authentication():
    client = APIClient()
    response = client.put("/api/available_rules/", {})
    assert response.status_code == 401


# Patch method


def test_AvailableRuleViewSet_patch(test_owner, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_owner)
    body = {
        "day_of_week": 7,
    }

    response = client.patch(f"/api/available_rules/{test_available_rule.id}/", body)
    test_available_rule.refresh_from_db()
    assert response.status_code == 200
    assert test_available_rule.day_of_week == body["day_of_week"]


def test_AvailableRuleViewSet_patch_not_found(test_owner, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_owner)

    # User provided not exist available_rule
    response = client.patch("/api/available_rules/not_exists/", {})
    assert response.status_code == 404


def test_AvailableRuleViewSet_patch_returns_404_for_non_owner(test_user, test_available_rule):
    """
    Restaurant in test_available_rule belong to test_owner so this endpoint should return 404
    for test_user because test_user has not any available_rules.
    """
    client = APIClient()
    client.force_authenticate(test_user)

    response = client.patch(f"/api/available_rules/{test_available_rule.id}/", {})
    assert response.status_code == 404


def test_AvailableRuleViewSet_patch_requires_authentication():
    client = APIClient()
    response = client.patch("/api/available_rules/", {})
    assert response.status_code == 401


# Delete Method
def test_AvailableRuleViewSet_delete(test_owner, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.delete(f"/api/available_rules/{test_available_rule.id}/")
    assert response.status_code == 204
    assert not AvailableRule.objects.filter(id=test_available_rule.id).exists()


def test_AvailableRuleViewSet_delete_not_found(test_owner, test_available_rule):
    client = APIClient()
    client.force_authenticate(test_owner)

    # User provided not exist available_rule
    response = client.delete("/api/available_rules/not_exists/")
    assert response.status_code == 404


def test_AvailableRuleViewSet_delete_requires_authentication():
    client = APIClient()
    response = client.delete("/api/available_rules/")
    assert response.status_code == 401


# test for api/available_rules/restaurant_table/


# Post method
def test_RestaurantTableViewSet_post(test_owner, test_restaurant):
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


def test_RestaurantTableViewSet_post_not_owner(test_user, test_restaurant):
    """
    User in this test are not owner of provided restaurant.
    """
    client = APIClient()
    client.force_authenticate(test_user)
    body = {
        "restaurant": test_restaurant.id,
        "table_number": "A1",
        "seats": 4,
    }
    response = client.post("/api/available_rules/restaurant_table/", body)
    assert response.status_code == 403


def test_RestaurantTableViewSet_post_requires_authentication():
    client = APIClient()
    response = client.post("/api/available_rules/restaurant_table/")
    assert response.status_code == 401


# Get method
def test_RestaurantTableViewSet_get(test_owner, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get("/api/available_rules/restaurant_table/")
    assert response.status_code == 200
    assert len(response.data) == 1


def test_RestaurantTableViewSet_get_details(test_owner, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/")
    assert response.status_code == 200


def test_RestaurantTableViewSet_get_returns_404_for_non_owner(test_user, test_restaurant_table):
    """
    This endpoint should not return any tabel for test_user because test_user has not any tabel
    test_restaurant_table has restaurant that belong to test_owner.
    """
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get(f"/api/available_rules/restaurant_table/{test_restaurant_table.id}/")
    assert response.status_code == 404


def test_RestaurantTableViewSet_get_not_exist_table(test_owner, test_restaurant_table):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get("/api/available_rules/restaurant_table/not_exist_table/")
    assert response.status_code == 404


# Put method
def test_RestaurantTableViewSet_put(test_owner, test_restaurant_table):

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
