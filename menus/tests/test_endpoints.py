import pytest
from rest_framework import status
from rest_framework.test import APIClient

from menus.models import Dish, Menu

# Test for api/menus/dish/


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
        ({"name": "", "price": 129.10}, status.HTTP_400_BAD_REQUEST),
        # Missing price
        ({"name": "test_dish", "price": ""}, status.HTTP_400_BAD_REQUEST),
        # Not exist menu
        ({"name": "test_dish", "menu": 99999, "price": ""}, status.HTTP_400_BAD_REQUEST),
    ],
)
def test_DishViewSet_post_invalid_payload(test_owner, test_menu, payload, excepted_status):
    client = APIClient()
    client.force_authenticate(user=test_owner)
    payload["menu"] = payload.get("menu", test_menu.id)
    response = client.post("/api/menus/dish/", payload)
    assert response.status_code == excepted_status


# Patch method
def test_DishViewSet_patch_owner_of_restaurant(test_owner, test_dish):
    """
    test_owner is the owner of the restaurant that contains test_dish.
    So he has access to this endpoint.
    """
    client = APIClient()
    client.force_authenticate(user=test_owner)
    body = {"name": "new_name"}
    response = client.patch(f"/api/menus/dish/{test_dish.id}/", body)
    test_dish.refresh_from_db()
    assert response.status_code == 200
    assert test_dish.name == body["name"]


def test_DishViewSet_patch_manager_of_restaurant(test_membership_manager, test_dish):
    """
    In this test request user is the manager of the restaurant that contains test_dish.
    So he has access to this endpoint.
    """
    client = APIClient()
    client.force_authenticate(user=test_membership_manager.user)
    body = {"price": test_dish.price + 50}
    response = client.patch(f"/api/menus/dish/{test_dish.id}/", body)
    test_dish.refresh_from_db()
    assert response.status_code == 200
    assert test_dish.price == body["price"]


def test_DishViewSet_patch_staff_of_restaurant(test_membership_staff, test_dish):
    """
    In this test request user is only the staff of the restaurant so
    he does not have access to this endpoint.
    """
    client = APIClient()
    client.force_authenticate(user=test_membership_staff.user)
    response = client.patch(f"/api/menus/dish/{test_dish.id}/", {})
    assert response.status_code == 403


def test_DishViewSet_patch_normal_user(test_user, test_dish):
    client = APIClient()
    client.force_authenticate(user=test_user)
    response = client.patch(f"/api/menus/dish/{test_dish.id}/", {})
    assert response.status_code == 403


def test_DishViewSet_patch_requires_authentication():
    client = APIClient()
    response = client.patch("/api/menus/dish/", {})
    assert response.status_code == 401


def test_DishViewSet_patch_return_400_for_change_menu(test_owner, test_dish, test_menu_1):
    """
    Cannot change menu of already existing dish.
    """
    client = APIClient()
    client.force_authenticate(user=test_owner)
    body = {
        "menu": test_menu_1.id,
    }
    response = client.patch(f"/api/menus/dish/{test_dish.id}/", body)

    assert response.status_code == 400


# Delete method
def test_DishViewSet_delete_owner_of_restaurant(test_owner, test_dish):
    """
    In this test request user is the owner of the restaurant that contains test_dish.
    So he is allowed to delete a dish.
    """
    client = APIClient()
    client.force_authenticate(user=test_owner)
    response = client.delete(f"/api/menus/dish/{test_dish.id}/")
    assert response.status_code == 204
    assert not Dish.objects.filter(id=test_dish.id).exists()


def test_DishViewSet_delete_manager_of_restaurant(test_membership_manager, test_dish):
    """
    In this test request user is the manager of the restaurant that contains test_dish.
    So he is allowed to delete a dish.
    """
    client = APIClient()
    client.force_authenticate(user=test_membership_manager.user)
    response = client.delete(f"/api/menus/dish/{test_dish.id}/")
    assert response.status_code == 204
    assert not Dish.objects.filter(id=test_dish.id).exists()


def test_DishViewSet_delete_staff_of_restaurant(test_membership_staff, test_dish):
    """
    In this test request user is only the staff of the restaurant so
    he does not have access to this endpoint.
    """
    client = APIClient()
    client.force_authenticate(user=test_membership_staff.user)
    response = client.delete(f"/api/menus/dish/{test_dish.id}/")
    assert response.status_code == 403


def test_DishViewSet_delete_normal_user(test_user, test_dish):
    """
    In this test request user is just a normal user.
    So he does not have access to this endpoint.
    """
    client = APIClient()
    client.force_authenticate(user=test_user)
    response = client.delete(f"/api/menus/dish/{test_dish.id}/")
    assert response.status_code == 403


# Test for api/menus/
# Get details
def test_MenuViewSet_retrieve_normal_user(test_user, test_menu):
    """
    Each user has access to this endpoint.
    """
    client = APIClient()
    client.force_authenticate(user=test_user)
    response = client.get(f"/api/menus/{test_menu.id}/")
    assert response.status_code == 200


@pytest.mark.parametrize("filters", ["?ordering=price", "?ordering=-price"])
def test_MenuViewSet_retrieve_dishes_ordered_by_price(filters, test_user, test_menu):
    """
    In this test we create 2 dishes in test_menu and use tow available filters by price  and check whether
    endpoint will show us dishes in correct order.
    """
    client = APIClient()
    client.force_authenticate(user=test_user)
    # Creates dishes
    dish_1 = Dish.objects.create(name="dish_1", menu=test_menu, price=60)
    dish_2 = Dish.objects.create(name="dish_2", menu=test_menu, price=35)

    response = client.get(f"/api/menus/{test_menu.id}/{filters}")
    assert response.status_code == 200
    assert len(response.data["dishes"]) == 2

    if filters == "?ordering=price":
        # The first should be dish_2
        assert response.data["dishes"][0]["name"] == dish_2.name
        assert response.data["dishes"][0]["price"] == "35.00"

        # The second should be dish_1
        assert response.data["dishes"][1]["name"] == dish_1.name
        assert response.data["dishes"][1]["price"] == "60.00"
    if filters == "?ordering=-price":
        # The first should be dish_1
        assert response.data["dishes"][0]["name"] == dish_1.name
        assert response.data["dishes"][0]["price"] == "60.00"

        # The second should be dish_2
        assert response.data["dishes"][1]["name"] == dish_2.name
        assert response.data["dishes"][1]["price"] == "35.00"


# Post method
def test_MenuViewSet_post_owner_of_restaurant(test_owner, test_restaurant):
    """
    In this test request user is the owner of the restaurant.
    So he can create a menu along his restaurant.
    """
    client = APIClient()
    client.force_authenticate(user=test_owner)
    body = {
        "name": "test_menu",
        "restaurant": test_restaurant.id,
    }
    response = client.post("/api/menus/", body)
    assert response.status_code == 201
    assert Menu.objects.filter(restaurant=test_restaurant, name=body["name"]).exists()


def test_MenuViewSet_post_manager_of_restaurant(test_membership_manager, test_restaurant):
    """
    In this test request user is the manger of the restaurant.
    So he can create a menu along his restaurant.
    """
    client = APIClient()
    client.force_authenticate(user=test_membership_manager.user)
    body = {
        "name": "test_menu",
        "restaurant": test_restaurant.id,
    }
    response = client.post("/api/menus/", body)
    assert response.status_code == 201
    assert Menu.objects.filter(restaurant=test_restaurant, name=body["name"]).exists()


def test_MenuViewSet_post_staff_of_restaurant(test_membership_staff, test_restaurant):
    """
    Request user is the staff of the restaurant.
    So he does not have access to this endpoint.
    """
    client = APIClient()
    client.force_authenticate(user=test_membership_staff.user)
    body = {
        "name": "test_menu",
        "restaurant": test_restaurant.id,
    }
    response = client.post("/api/menus/", body)
    assert response.status_code == 403


def test_MenuViewSet_post_normal_user(test_user, test_restaurant):
    """
    Request user is the normal user.
    So he does not have access to this endpoint.
    """
    client = APIClient()
    client.force_authenticate(user=test_user)
    body = {
        "name": "test_menu",
        "restaurant": test_restaurant.id,
    }
    response = client.post("/api/menus/", body)
    assert response.status_code == 403


def test_MenuViewSet_post_requires_authentication():
    client = APIClient()
    response = client.post("/api/menus/", {})
    assert response.status_code == 401


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Missing name
        ({"name": ""}, status.HTTP_400_BAD_REQUEST),
        # Not exist restaurant
        ({"name": "test_name", "restaurant": 9999}, status.HTTP_400_BAD_REQUEST),
    ],
)
def test_MenuViewSet_post_invalid_data(payload, expected_status, test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(user=test_owner)
    payload["restaurant"] = payload.get("restaurant", test_restaurant.id)
    response = client.post("/api/menus/", payload)
    assert response.status_code == expected_status


# Patch method
def test_MenuViewSet_patch_owner_of_restaurant(test_owner, test_menu):
    """
    Request user is the owner of the restaurant.
    So he can change the menu along his restaurant.
    """
    client = APIClient()
    client.force_authenticate(user=test_owner)
    body = {
        "name": "new_menu",
    }
    response = client.patch(f"/api/menus/{test_menu.id}/", body)
    assert response.status_code == 200
    test_menu.refresh_from_db()
    assert test_menu.name == body["name"]


def test_MenuViewSet_patch_manger_of_restaurant(test_membership_manager, test_menu):
    """
    Request user is the manager of the restaurant.
    So he can change the menu along his restaurant.
    """
    client = APIClient()
    client.force_authenticate(user=test_membership_manager.user)
    body = {
        "name": "new_menu",
    }
    response = client.patch(f"/api/menus/{test_menu.id}/", body)
    assert response.status_code == 200
    test_menu.refresh_from_db()
    assert test_menu.name == body["name"]


def test_MenuViewSet_patch_staff_of_restaurant(test_membership_staff, test_menu):
    """
    Request user is the staff of the restaurant.
    So he does not have access to this endpoint.
    """
    client = APIClient()
    client.force_authenticate(user=test_membership_staff.user)
    response = client.patch(f"/api/menus/{test_menu.id}/", {})
    assert response.status_code == 403


def test_MenuViewSet_patch_normal_user(test_user, test_menu):
    client = APIClient()
    client.force_authenticate(user=test_user)
    response = client.patch(f"/api/menus/{test_menu.id}/", {})
    assert response.status_code == 403


def test_MenuViewSet_patch_requires_authentication():
    client = APIClient()
    response = client.patch("/api/menus/", {})
    assert response.status_code == 401


def test_MenuViewSet_patch_returns_400_for_changing_restaurant(test_owner, test_menu, test_restaurant_1):
    """
    Cannot change the restaurant of already existing menu.
    """
    client = APIClient()
    client.force_authenticate(user=test_owner)
    body = {
        "name": "new_menu",
        "restaurant": test_restaurant_1.id,
    }
    response = client.patch(f"/api/menus/{test_menu.id}/", body)
    assert response.status_code == 400


# Delete method
def test_MenuViewSet_delete_owner_of_restaurant(test_owner, test_menu):
    client = APIClient()
    client.force_authenticate(user=test_owner)
    response = client.delete(f"/api/menus/{test_menu.id}/")
    assert response.status_code == 204
    assert not Menu.objects.filter(id=test_menu.id).exists()


def test_MenuViewSet_delete_manager_of_restaurant(test_membership_manager, test_menu):
    client = APIClient()
    client.force_authenticate(user=test_membership_manager.user)
    response = client.delete(f"/api/menus/{test_menu.id}/")
    assert response.status_code == 204
    assert not Menu.objects.filter(id=test_menu.id).exists()


def test_MenuViewSet_delete_staff_of_restaurant(test_membership_staff, test_menu):
    client = APIClient()
    client.force_authenticate(user=test_membership_staff.user)
    response = client.delete(f"/api/menus/{test_menu.id}/")
    assert response.status_code == 403


def test_MenuViewSet_delete_normal_user(test_user, test_menu):
    client = APIClient()
    client.force_authenticate(user=test_user)
    response = client.delete(f"/api/menus/{test_menu.id}/")
    assert response.status_code == 403


def test_MenuViewSet_delete_requires_authentication():
    client = APIClient()
    response = client.delete("/api/menus/")
    assert response.status_code == 401
