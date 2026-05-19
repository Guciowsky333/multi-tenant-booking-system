import pytest

from accounts.models import CustomUser
from restaurants.models import CuisineType, Restaurant


@pytest.fixture
def test_user(db):
    return CustomUser.objects.create_user(email="test@test.com", password="Test_password")


@pytest.fixture
def test_user_2(db):
    return CustomUser.objects.create_user(email="test2@test.com", password="Test_password2")


@pytest.fixture
def test_cuisine_type(db):
    return CuisineType.objects.create(name="test_cuisine_type_1", id=1)


@pytest.fixture
def test_cuisine_type_2(db):
    return CuisineType.objects.create(name="test_cuisine_type_2", id=2)


@pytest.fixture
def test_exist_restaurant(db, test_cuisine_type, test_user):
    return Restaurant.objects.create(
        name="test_exist_restaurant",
        owner=test_user,
        cuisine_type=test_cuisine_type,
        address="test address",
        city="test city",
    )
