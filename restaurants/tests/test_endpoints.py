import pytest
from rest_framework.test import APIClient

from restaurants.models import CuisineType, Restaurant
from user_reviews.models import Review


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


# Get method
def test_RestaurantViewSet_get(test_user, test_cuisine_type):
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
    response = client.get("/api/restaurants/?page=1")
    assert response.status_code == 200
    assert len(response.data["results"]) == 2


def test_RestaurantViewSet_get_returns_average_rating(test_user, test_user_1, test_restaurant):
    """
    In this test we create 2 reviews of test_restaurant and check whether our endpoint
    show us average rating correct.

    The first review has 8 rating and the second has 7 so our average rating should be 7.5
    """
    # First review
    Review.objects.create(
        restaurant=test_restaurant,
        user=test_user,
        rating=8,
    )
    # Second review
    Review.objects.create(
        restaurant=test_restaurant,
        user=test_user_1,
        rating=7,
    )
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get("/api/restaurants/?page=1")
    assert response.status_code == 200
    restaurant = response.data["results"][0]
    assert restaurant["average_review_rating"] == 7.5


def test_RestaurantViewSet_get_filter_by_city(test_user_1, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_user_1)
    response = client.get(f"/api/restaurants/?city={test_restaurant.city}")
    assert response.status_code == 200


def test_RestaurantViewSet_get_requires_authentication():
    client = APIClient()
    response = client.get("/api/restaurants/")
    assert response.status_code == 401


def test_RestaurantViewSet_get_details(test_user, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get(f"/api/restaurants/{test_restaurant.id}/")
    assert response.status_code == 200

    assert response.data["name"] == test_restaurant.name
    assert response.data["address"] == test_restaurant.address
    assert response.data["city"] == test_restaurant.city


def test_RestaurantViewSet_get_details_invalid_id(test_user):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get(f"/api/restaurants/{404}/")
    assert response.status_code == 404


def test_RestaurantViewSet_get_details_authentication(test_restaurant):
    client = APIClient()
    response = client.get(f"/api/restaurants/{test_restaurant.id}/")
    assert response.status_code == 401


# Post method
def test_RestaurantViewSet_post(test_user, test_cuisine_type):
    """
    Checks if this endpoint correctly creates a new Restaurant
    """
    client = APIClient()
    client.force_authenticate(test_user)

    body = {
        "name": "test_restaurant_1",
        "cuisine_type": f"{test_cuisine_type.id}",
        "address": "test_address",
        "city": "test_city",
    }

    response = client.post("/api/restaurants/", body)
    print(response.data)
    assert response.status_code == 201

    assert Restaurant.objects.filter(name=body["name"]).exists()


@pytest.mark.parametrize(
    "payload, excepted_status",
    [
        # Missing name
        ({"name": "", "cuisine_type": 1, "address": "test_address", "city": "test_city"}, 400),
        # Missing cuisine_type
        ({"name": "test_restaurant_1", "cuisine_type": "", "address": "test_address", "city": "test_city"}, 400),
        # Missing address
        ({"name": "test_restaurant_1", "cuisine_type": 1, "address": "", "city": "test_city"}, 400),
        # Missing city
        ({"name": "test_restaurant_1", "cuisine_type": 1, "address": "test_address", "city": ""}, 400),
        # Provided name already exist
        ({"name": "test_restaurant", "cuisine_type": 1, "address": "test_address", "city": "test_city"}, 400),
    ],
)
def test_RestaurantViewSet_post_invalid_data(payload, excepted_status, test_user, test_restaurant, test_cuisine_type):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.post("/api/restaurants/", payload)
    assert response.status_code == excepted_status


def test_RestaurantViewSet_requires_authentication():
    client = APIClient()
    response = client.post("/api/restaurants/")
    assert response.status_code == 401


# Put method
def test_RestaurantViewSet_put_owner(test_owner, test_restaurant, test_cuisine_type):
    """
    Only owner or member with manager role have access to this endpoint
    """

    client = APIClient()
    client.force_authenticate(test_owner)

    body = {
        "name": "changed_name",
        "cuisine_type": f"{test_cuisine_type.id}",
        "address": "changed_address",
        "city": "changed_city",
    }

    response = client.put(f"/api/restaurants/{test_restaurant.id}/", body)
    test_restaurant.refresh_from_db()
    assert response.status_code == 200

    # Checks whether data has been changed correctly
    assert test_restaurant.name == body["name"]
    assert test_restaurant.address == body["address"]
    assert test_restaurant.city == body["city"]


def test_RestaurantViewSet_put_manager(test_membership_manager, test_restaurant, test_cuisine_type_2):
    """
    Only owner or member with manager role have access to this endpoint
    """
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)

    body = {
        "name": "changed_name",
        "cuisine_type": f"{test_cuisine_type_2.id}",
        "address": "changed_address",
        "city": "changed_city",
    }
    response = client.put(f"/api/restaurants/{test_restaurant.id}/", body)
    assert response.status_code == 200


def test_RestaurantViewSet_put_staff(test_membership_staff, test_restaurant, test_cuisine_type_2):
    """
    Member with staff role does not have access to this endpoint
    """
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)

    response = client.put(f"/api/restaurants/{test_restaurant.id}/", {})
    assert response.status_code == 403


def test_RestaurantViewSet_put_not_owner_or_manager(test_user_2, test_restaurant):
    """
    Normal user does not have access to this endpoint
    """
    client = APIClient()
    client.force_authenticate(test_user_2)

    response = client.put(f"/api/restaurants/{test_restaurant.id}/", {})
    assert response.status_code == 403


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
def test_RestaurantViewSet_put_invalid_data(payload, excepted_status, test_owner, test_cuisine_type, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.put(f"/api/restaurants/{test_restaurant.id}/", payload)
    assert response.status_code == excepted_status


def test_RestaurantViewSet_put_requires_authentication():
    client = APIClient()
    response = client.put("/api/restaurants/")
    assert response.status_code == 401


# Patch method
def test_RestaurantViewSet_patch_owner(test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)

    body = {
        "name": "changed_name",
    }
    response = client.patch(f"/api/restaurants/{test_restaurant.id}/", body)
    test_restaurant.refresh_from_db()
    assert response.status_code == 200
    assert test_restaurant.name == body["name"]


def test_RestaurantViewSet_patch_manager(test_membership_manager, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    body = {
        "name": "changed_name",
    }
    response = client.patch(f"/api/restaurants/{test_restaurant.id}/", body)
    test_restaurant.refresh_from_db()
    assert response.status_code == 200
    assert test_restaurant.name == body["name"]


def test_RestaurantViewSet_patch_staff(test_membership_staff, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    response = client.patch(f"/api/restaurants/{test_restaurant.id}/", {})
    assert response.status_code == 403


def test_RestaurantViewSet_patch_not_owner_or_manager(test_user_2, test_restaurant):
    """
    Only the owner of provided restaurant has access to this action
    """
    client = APIClient()
    client.force_authenticate(test_user_2)
    response = client.patch(f"/api/restaurants/{test_restaurant.id}/", {})
    assert response.status_code == 403


def test_RestaurantViewSet_patch_requires_authentication():
    client = APIClient()
    response = client.put("/api/restaurants/")
    assert response.status_code == 401


# Delete method
"""
Only owner is allowed to delete his own restaurant 
"""


def test_RestaurantViewSet_delete_owner(test_owner, test_restaurant):

    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.delete(f"/api/restaurants/{test_restaurant.id}/")
    assert response.status_code == 204
    assert not Restaurant.objects.filter(id=test_restaurant.id).exists()


def test_RestaurantViewSet_delete_manager(test_membership_manager, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    response = client.delete(f"/api/restaurants/{test_restaurant.id}/")
    assert response.status_code == 403


def test_RestaurantViewSet_delete_staff(test_membership_staff, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_membership_staff.user)
    response = client.delete(f"/api/restaurants/{test_restaurant.id}/")
    assert response.status_code == 403


def test_RestaurantViewSet_delete_not_owner(test_user_2, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_user_2)
    response = client.delete(f"/api/restaurants/{test_restaurant.id}/")
    assert response.status_code == 403


def test_RestaurantViewSet_delete_requires_authentication():
    client = APIClient()
    response = client.delete("/api/restaurants/")
    assert response.status_code == 401
