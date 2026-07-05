from datetime import timedelta

import pytest
from django.utils import timezone

from available_rules.models import AvailableRule, RestaurantBreak, RestaurantException, RestaurantTable


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


@pytest.fixture
def test_restaurant_break(db, test_restaurant):
    return RestaurantBreak.objects.create(restaurant=test_restaurant, start="9:30", end="10:00", day_of_week=1)


@pytest.fixture
def test_exist_break(db, test_restaurant):
    return RestaurantBreak.objects.create(restaurant=test_restaurant, start="18:00", end="18:30", day_of_week=1)


@pytest.fixture
def test_restaurant_exception(db, test_restaurant):
    tomorrow = (timezone.now() + timedelta(days=1)).date().isoformat()
    return RestaurantException.objects.create(
        restaurant=test_restaurant,
        date=tomorrow,
        type="special_hours",
        opening_time="10:00",
        closing_time="20:00",
    )
