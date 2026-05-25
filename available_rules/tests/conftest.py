import pytest

from accounts.models import CustomUser
from available_rules.models import AvailableRule, RestaurantTable
from restaurants.models import CuisineType, Restaurant


@pytest.fixture
def test_user(db):
    return CustomUser.objects.create_user(email="test@.com", password="Test_password")


@pytest.fixture
def test_owner(db):
    return CustomUser.objects.create_user(email="test@test.com", password="Test_password")


@pytest.fixture
def test_cuisine_type(db):
    return CuisineType.objects.create(name="test_cuisine_type")


@pytest.fixture
def test_restaurant(db, test_owner, test_cuisine_type):
    return Restaurant.objects.create(
        id=1,
        name="test_restaurant",
        address="test_address",
        city="test_city",
        owner=test_owner,
        cuisine_type=test_cuisine_type,
    )


@pytest.fixture
def test_available_rule(db, test_restaurant, test_cuisine_type):
    return AvailableRule.objects.create(
        restaurant=test_restaurant,
        day_of_week=1,
        opening_time="8:00",
        closing_time="22:00",
    )


@pytest.fixture
def test_restaurant_table(db, test_restaurant):
    return RestaurantTable.objects.create(restaurant=test_restaurant, table_number="A10", seats=4)
