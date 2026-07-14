import pytest

from accounts.models import CustomUser, VerificationCode
from available_rules.models import AvailableRule, RestaurantBreak, RestaurantException, RestaurantTable
from booking_system.tests.test_endpoints import next_monday
from memberships.models import MemberShip
from restaurants.models import CuisineType, Restaurant
from user_reviews.models import Review


@pytest.fixture
def test_owner(db):
    return CustomUser.objects.create_user(email="test@test.com", password="Test_password")


@pytest.fixture
def test_owner_1(db):
    return CustomUser.objects.create_user(email="test1@test1.com", password="Test_password")


@pytest.fixture
def test_user(db):
    return CustomUser.objects.create_user(email="test@test1.com", password="Test_password")


@pytest.fixture
def test_user_1(db):
    return CustomUser.objects.create_user(email="test@test2.com", password="Test_password")


@pytest.fixture
def test_user_2(db):
    return CustomUser.objects.create_user(email="test@test3.com", password="Test_password")


@pytest.fixture
def test_verification_code(db):
    return VerificationCode.objects.create(email="test@test1.com", code="123456")


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
def test_restaurant_1(db, test_owner_1, test_cuisine_type):
    return Restaurant.objects.create(
        id=2,
        name="test_restaurant_1",
        address="test_address",
        city="test_city",
        owner=test_owner_1,
        cuisine_type=test_cuisine_type,
    )


@pytest.fixture
def test_membership_manager(db, test_restaurant, test_user):
    return MemberShip.objects.create(
        restaurant=test_restaurant,
        user=test_user,
        role="manager",
    )


@pytest.fixture
def test_membership_staff(db, test_restaurant, test_user_1):
    return MemberShip.objects.create(
        restaurant=test_restaurant,
        user=test_user_1,
        role="staff",
    )


@pytest.fixture
def test_review_1(db, test_restaurant, test_user):
    return Review.objects.create(
        user=test_user,
        restaurant=test_restaurant,
        rating=8,
        comment="Test comment",
    )


@pytest.fixture
def test_review_2(db, test_restaurant, test_user_1):
    return Review.objects.create(
        user=test_user_1,
        restaurant=test_restaurant,
        rating=7,
        comment="Test comment",
    )


@pytest.fixture
def test_available_rule(db, test_restaurant, test_cuisine_type):
    return AvailableRule.objects.create(
        restaurant=test_restaurant,
        day_of_week=1,
        opening_time="08:00:00",
        closing_time="22:00:00",
    )


@pytest.fixture
def test_restaurant_table(db, test_restaurant):
    return RestaurantTable.objects.create(restaurant=test_restaurant, table_number="A10", seats=4)


@pytest.fixture
def test_restaurant_break(db, test_restaurant):
    return RestaurantBreak.objects.create(restaurant=test_restaurant, start="09:30:00", end="10:00:00", day_of_week=1)


@pytest.fixture
def test_exception_special_hours(db, test_restaurant):
    return RestaurantException.objects.create(
        restaurant=test_restaurant,
        date=next_monday(),
        type="special_hours",
        opening_time="10:00:00",
        closing_time="20:00:00",
    )


@pytest.fixture
def test_exception_closed(db, test_restaurant):
    return RestaurantException.objects.create(
        restaurant=test_restaurant,
        date=next_monday(),
        type="closed",
        opening_time="10:00:00",
        closing_time="20:00:00",
    )
