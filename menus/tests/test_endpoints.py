import pytest
from rest_framework import status
from rest_framework.test import APIClient

from menus.models import Dish

# test for api/menus/dish/


# Post method
def test_DishViewSet_post_owner_of_restaurant(test_menu, test_owner):
    """
    Only owner or manager are allowed to create dishes along their restaurant.
    """
    client = APIClient()
    # test_owner is the owner of the restaurant that contains test_menu.
    client.force_authenticate(user=test_owner)
    body = {"menu": test_menu.id, "name": "test_dish", "price": 129.10}
    response = client.post("/api/menus/dish/", body)
    assert response.status_code == 201
    assert Dish.objects.filter(menu=test_menu, name="test_dish").exists()


def test_DishViewSet_post_manager_of_restaurant(test_membership_manager, test_menu):
    """
    Only owner or manager are allowed to create dishes along their restaurant.
    """
    client = APIClient()
    # test_membership_manager is the manager of the restaurant that contains test_menu.
    client.force_authenticate(user=test_membership_manager.user)
    body = {"menu": test_menu.id, "name": "test_dish", "price": 129.10}
    response = client.post("/api/menus/dish/", body)
    assert response.status_code == 201
    assert Dish.objects.filter(menu=test_menu, name="test_dish").exists()


def test_DishViewSet_post_staff_of_restaurant(test_membership_staff, test_menu):
    """
    Members of the restaurant with status "staff" are not allowed to create dishes.
    """
    client = APIClient()
    client.force_authenticate(user=test_membership_staff.user)
    body = {"menu": test_menu.id, "name": "test_dish", "price": 129.10}
    response = client.post("/api/menus/dish/", body)
    assert response.status_code == 403


def test_DishViewSet_post_owner_of_different_restaurant(test_owner, test_restaurant, test_menu_1):
    """
    test_owner is the owner of test_restaurant it is different restaurant than contains test_menu_1.So endpoint should return 403.
    """
    client = APIClient()
    client.force_authenticate(user=test_owner)
    body = {"menu": test_menu_1.id, "name": "test_dish", "price": 19.10}
    response = client.post("/api/menus/dish/", body)
    assert response.status_code == 403


def test_DishViewSet_post_normal_user(test_user, test_menu):
    client = APIClient()
    client.force_authenticate(user=test_user)
    body = {"menu": test_menu.id, "name": "test_dish", "price": 129.10}
    response = client.post("/api/menus/dish/", body)
    assert response.status_code == 403


def test_DishViewSet_post_requires_authentication():
    client = APIClient()
    response = client.post("/api/menus/dish/", {})
    assert response.status_code == 401


@pytest.mark.parametrize(
    "payload, excepted_status",
    # menu id 1 = test_menu.id in file conftest.py
    [
        # Missing name
        ({"name": "", "menu": 1, "price": 129.10}, status.HTTP_400_BAD_REQUEST),
        # Missing menu
        ({"name": "test_dish", "menu": "", "price": 129.10}, status.HTTP_400_BAD_REQUEST),
        # Missing price
        ({"name": "test_dish", "menu": 1, "price": ""}, status.HTTP_400_BAD_REQUEST),
        # Not exist menu
        ({"name": "test_dish", "menu": 99999, "price": ""}, status.HTTP_400_BAD_REQUEST),
    ],
)
def test_DishViewSet_post_invalid_payload(test_owner, test_menu, payload, excepted_status):
    client = APIClient()
    client.force_authenticate(user=test_owner)
    response = client.post("/api/menus/dish/", payload)
    assert response.status_code == excepted_status
