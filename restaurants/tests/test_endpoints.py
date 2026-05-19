import pytest
from rest_framework.test import APIClient

from restaurants.models import CuisineType, Restaurant


# Test for api/restaurants/all_cuisine_type/
@pytest.mark.django_db
def test_AllCuisinesTypeView(test_user):
    """
    In this test we create 2 example CuisineType models, and check whether
    our endpoint show us them correctly.
    """

    CuisineType.objects.create(
        name="test_cuisine_type_1",
    )
    CuisineType.objects.create(
        name="test_cuisine_type_2",
    )

    client = APIClient()
    client.force_authenticate(test_user)

    response = client.get("/api/restaurants/all_cuisine_type/")
    assert response.status_code == 200
    assert response.data["message"] == "All allowed cuisines types"
    # Check if in response we have exactly 2 CuisineType
    assert len(response.data["cuisine_types"]) == 2


def test_AllCuisinesTypeView_requires_authentication():
    client = APIClient()
    response = client.get("/api/restaurants/all_cuisine_type/")
    assert response.status_code == 401


# Test for api/restaurants/


# List
def test_RestaurantViewSet_list(test_user, test_cuisine_type):
    """
    In this test we create 2 example Restaurant models, and check whether
    endpoint show us them correctly.
    """
    Restaurant.objects.create(
        name="test_restaurant_1",
        owner=test_user,
        cuisine_type=test_cuisine_type,
        address="test_address_1",
        city="test_city_1",
    )

    Restaurant.objects.create(
        name="test_restaurant_2",
        owner=test_user,
        cuisine_type=test_cuisine_type,
        address="test_address_2",
        city="test_city_2",
    )

    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get("/api/restaurants/")
    assert response.status_code == 200
    assert len(response.data) == 2


def test_RestaurantViewSet_list_requires_authentication():
    client = APIClient()
    response = client.get("/api/restaurants/")
    assert response.status_code == 401


# Retrieve
def test_RestaurantViewSet_retrieve(test_user, test_exist_restaurant):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get(f"/api/restaurants/{test_exist_restaurant.id}/")
    assert response.status_code == 200

    assert response.data["name"] == test_exist_restaurant.name
    assert response.data["address"] == test_exist_restaurant.address
    assert response.data["city"] == test_exist_restaurant.city


def test_RestaurantViewSet_retrieve_invalid_id(test_user):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get(f"/api/restaurants/{404}/")
    assert response.status_code == 404


def test_RestaurantViewSet_retrieve_requires_authentication(test_exist_restaurant):
    client = APIClient()
    response = client.get(f"/api/restaurants/{test_exist_restaurant.id}/")
    assert response.status_code == 401


# Create
def test_RestaurantViewSet_post(test_user, test_cuisine_type):
    """
    Checks if this endpoint correctly creates a new Restaurant
    """
    client = APIClient()
    client.force_authenticate(test_user)

    body = {
        "name": "test_restaurant",
        "cuisine_type": f"{test_cuisine_type.id}",
        "address": "test_address",
        "city": "test_city",
    }

    response = client.post("/api/restaurants/", body)
    assert response.status_code == 201

    assert Restaurant.objects.filter(name="test_restaurant").exists()


@pytest.mark.parametrize(
    "payload, excepted_status",
    [
        # Missing name
        ({"name": "", "cuisine_type": 1, "address": "test_address", "city": "test_city"}, 400),
        # Missing cuisine_type
        ({"name": "test_restaurant", "cuisine_type": "", "address": "test_address", "city": "test_city"}, 400),
        # Missing address
        ({"name": "test_restaurant", "cuisine_type": 1, "address": "", "city": "test_city"}, 400),
        # Missing city
        ({"name": "test_restaurant", "cuisine_type": 1, "address": "test_address", "city": ""}, 400),
        # Provided name already exist
        ({"name": "test_exist_restaurant", "cuisine_type": 1, "address": "test_address", "city": "test_city"}, 400),
    ],
)
def test_RestaurantViewSet_post_invalid_data(
    payload, excepted_status, test_user, test_exist_restaurant, test_cuisine_type
):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.post("/api/restaurants/", payload)
    assert response.status_code == excepted_status


def test_RestaurantViewSet_requires_authentication():
    client = APIClient()
    response = client.post("/api/restaurants/")
    assert response.status_code == 401


# Update
def test_RestaurantViewSet_put(test_user, test_exist_restaurant, test_cuisine_type_2):
    client = APIClient()
    client.force_authenticate(test_user)

    body = {
        "name": "changed_name",
        "cuisine_type": f"{test_cuisine_type_2.id}",
        "address": "changed_address",
        "city": "changed_city",
    }

    response = client.put(f"/api/restaurants/{test_exist_restaurant.id}/", body)
    test_exist_restaurant.refresh_from_db()
    assert response.status_code == 200

    # Checks whether data has been changed correctly
    assert test_exist_restaurant.name == body["name"]
    assert test_exist_restaurant.address == body["address"]
    assert test_exist_restaurant.city == body["city"]


@pytest.mark.parametrize(
    "payload, excepted_status",
    [
        # Missing name
        ({"name": "", "cuisine_type": 1, "address": "test_address", "city": "test_city"}, 400),
        # Missing cuisine_type
        ({"name": "test_restaurant", "cuisine_type": "", "address": "test_address", "city": "test_city"}, 400),
        # Missing address
        ({"name": "test_restaurant", "cuisine_type": 1, "address": "", "city": "test_city"}, 400),
        # Missing city
        ({"name": "test_restaurant", "cuisine_type": 1, "address": "test_address", "city": ""}, 400),
        # Provided cuisine_type not exist
        ({"name": "test_restaurant", "cuisine_type": 3, "address": "test_address", "city": "test_city"}, 400),
    ],
)
def test_RestaurantViewSet_put_invalid_data(
    payload, excepted_status, test_user, test_cuisine_type, test_exist_restaurant
):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.put(f"/api/restaurants/{test_exist_restaurant.id}/", payload)
    assert response.status_code == excepted_status


def test_RestaurantViewSet_put_not_owner(test_user_2, test_exist_restaurant):
    """
    Only the owner of provided restaurant has access to this action
    """
    client = APIClient()
    client.force_authenticate(test_user_2)

    response = client.put(f"/api/restaurants/{test_exist_restaurant.id}/", {})
    assert response.status_code == 403


def test_RestaurantViewSet_put_requires_authentication():
    client = APIClient()
    response = client.put("/api/restaurants/")
    assert response.status_code == 401


# Partial_update
def test_RestaurantViewSet_patch(test_user, test_exist_restaurant):
    client = APIClient()
    client.force_authenticate(test_user)

    body = {
        "name": "changed_name",
    }
    response = client.patch(f"/api/restaurants/{test_exist_restaurant.id}/", body)
    test_exist_restaurant.refresh_from_db()
    assert response.status_code == 200

    # Checks whether name has been changed correctly
    assert test_exist_restaurant.name == body["name"]


def test_RestaurantViewSet_patch_not_owner(test_user_2, test_exist_restaurant):
    """
    Only the owner of provided restaurant has access to this action
    """
    client = APIClient()
    client.force_authenticate(test_user_2)
    response = client.patch(f"/api/restaurants/{test_exist_restaurant.id}/", {})
    assert response.status_code == 403


def test_RestaurantViewSet_patch_requires_authentication():
    client = APIClient()
    response = client.put("/api/restaurants/")
    assert response.status_code == 401


# Destroy
def test_RestaurantViewSet_delete(test_user, test_exist_restaurant):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.delete(f"/api/restaurants/{test_exist_restaurant.id}/")
    assert response.status_code == 204

    # Checks whether provided restaurant has been removed correctly
    assert not Restaurant.objects.filter(id=test_exist_restaurant.id).exists()


def test_RestaurantViewSet_delete_not_owner(test_user_2, test_exist_restaurant):
    client = APIClient()
    client.force_authenticate(test_user_2)
    response = client.delete(f"/api/restaurants/{test_exist_restaurant.id}/")
    assert response.status_code == 403


def test_RestaurantViewSet_delete_requires_authentication():
    client = APIClient()
    response = client.delete("/api/restaurants/")
    assert response.status_code == 401
