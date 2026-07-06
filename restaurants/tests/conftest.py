import pytest
from django.core.cache import cache

from restaurants.models import CuisineType


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def test_cuisine_type_2(db):
    return CuisineType.objects.create(name="test_cuisine_type_2")
