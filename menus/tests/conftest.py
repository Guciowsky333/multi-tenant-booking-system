import pytest

from menus.models import Dish, Menu


@pytest.fixture
def test_menu(test_restaurant):
    return Menu.objects.create(name="test_menu", restaurant=test_restaurant)


@pytest.fixture
def test_menu_1(test_restaurant_1):
    return Menu.objects.create(name="test_menu_1", restaurant=test_restaurant_1)


@pytest.fixture
def test_dish(test_menu):
    return Dish.objects.create(name="test_dish", menu=test_menu, price=100)
