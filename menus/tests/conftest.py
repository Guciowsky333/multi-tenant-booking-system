import pytest

from menus.models import Menu


@pytest.fixture
def test_menu(test_restaurant):
    return Menu.objects.create(id=1, name="test_menu", restaurant=test_restaurant)


@pytest.fixture
def test_menu_1(test_restaurant_1):
    return Menu.objects.create(id=2, name="test_menu_1", restaurant=test_restaurant_1)
