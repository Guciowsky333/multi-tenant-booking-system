import pytest

from restaurants.models import CuisineType


@pytest.fixture
def test_cuisine_type_2(db):
    return CuisineType.objects.create(name="test_cuisine_type_2")
