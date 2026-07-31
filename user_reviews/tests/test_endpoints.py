import pytest
from rest_framework import status
from rest_framework.test import APIClient

from user_reviews.models import Review

# Test list api/user_reviews/


def test_ReviewViewSet_get(test_user, test_review_1, test_review_2):
    """
    test_user has writen 1 review so our endpoint should return only 1 review of this user
    without test_review_2 because this review don't belong to test_user
    """
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get("/api/user_reviews/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


def test_ReviewViewSet_get_requires_authentication():
    client = APIClient()
    response = client.get("/api/user_reviews/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_ReviewViewSet_get_details(test_user, test_review_1):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get(f"/api/user_reviews/{test_review_1.id}/")
    assert response.status_code == status.HTTP_200_OK


def test_ReviewViewSet_get_details_not_owner_return_404(test_user_1, test_review_1):
    """
    test_user_1 is not the owner of test_review_1 so endpoint should return 404
    for someone who is not owner of provided review.
    """
    client = APIClient()
    client.force_authenticate(test_user_1)
    response = client.get(f"/api/user_reviews/{test_review_1.id}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_ReviewViewSet_get_details_invalid_id(test_user, test_review_1):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get("/api/user_reviews/invalid_id/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Test post api/user_reviews/
def test_ReviewViewSet_post(test_user, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_user)
    body = {"restaurant": test_restaurant.id, "rating": 8, "comment": "Test comment"}
    response = client.post("/api/user_reviews/", body)
    assert response.status_code == status.HTTP_201_CREATED
    assert Review.objects.filter(user=test_user, restaurant=test_restaurant, comment="Test comment").exists()


def test_ReviewViewSet_post_unique_review_per_restaurant(test_user, test_restaurant):
    """
    Each user can add only one review per restaurant.

    In this test test_user has already written a
    review of test_restaurant and is trying to write another one.
    """
    client = APIClient()
    client.force_authenticate(test_user)
    Review.objects.create(user=test_user, restaurant=test_restaurant, rating=8)
    body = {"restaurant": test_restaurant.id, "rating": 6, "comment": "Test comment 2"}
    response = client.post("/api/user_reviews/", body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Missing restaurant
        ({"restaurant": "", "rating": 2}, status.HTTP_400_BAD_REQUEST),
        # Missing rating
        ({"restaurant": "1", "rating": ""}, status.HTTP_400_BAD_REQUEST),
        # Not exist restaurant
        ({"restaurant": "Not_exist", "rating": 10}, status.HTTP_400_BAD_REQUEST),
        # too high rating max = 10
        ({"restaurant": "1", "rating": 11}, status.HTTP_400_BAD_REQUEST),
        # too low rating min = 1
        ({"restaurant": "1", "rating": 0}, status.HTTP_400_BAD_REQUEST),
    ],
)
def test_ReviewViewSet_post_invalid_data(test_user, test_restaurant, payload, expected_status):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.post("/api/user_reviews/", payload)
    assert response.status_code == expected_status


def test_ReviewViewSet_post_requires_authentication():
    client = APIClient()
    response = client.get("/api/user_reviews/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test put api/user_reviews/
def test_ReviewViewSet_put_review_owner(test_user, test_restaurant, test_review_1):
    client = APIClient()
    client.force_authenticate(test_user)
    body = {"restaurant": test_restaurant.id, "rating": 1, "comment": "New comment"}
    response = client.put(f"/api/user_reviews/{test_review_1.id}/", body)
    test_review_1.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert test_review_1.rating == body["rating"]
    assert test_review_1.comment == body["comment"]


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Missing restaurant
        ({"restaurant": "", "rating": 2}, status.HTTP_400_BAD_REQUEST),
        # Missing rating
        ({"restaurant": "1", "rating": ""}, status.HTTP_400_BAD_REQUEST),
        # Not exist restaurant
        ({"restaurant": "Not_exist", "rating": 10}, status.HTTP_400_BAD_REQUEST),
        # too high rating max = 10
        ({"restaurant": "1", "rating": 11}, status.HTTP_400_BAD_REQUEST),
        # too low rating min = 1
        ({"restaurant": "1", "rating": 0}, status.HTTP_400_BAD_REQUEST),
    ],
)
def test_ReviewViewSet_put_invalid_data(test_user, test_restaurant, test_review_1, payload, expected_status):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.put(f"/api/user_reviews/{test_review_1.id}/", payload)
    assert response.status_code == expected_status


def test_ReviewViewSet_put_return_404_for_not_owner(test_user, test_restaurant, test_review_2):
    """
    In this test test_user is not owner of test_review_2
    so endpoints should return 404 for someone who is not the owner.
    """
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.put(f"/api/user_reviews/{test_review_2.id}/", {})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_ReviewViewSet_put_requires_authentication():
    client = APIClient()
    response = client.put("/api/user_reviews/", {})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test patch api/user_reviews/
def test_ReviewViewSet_patch_review_owner(test_user, test_restaurant, test_review_1):
    client = APIClient()
    client.force_authenticate(test_user)
    body = {"comment": "New comment"}
    response = client.patch(f"/api/user_reviews/{test_review_1.id}/", body)
    test_review_1.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert test_review_1.comment == body["comment"]


def test_ReviewViewSet_patch_return_404_for_not_owner(test_user, test_restaurant, test_review_2):
    """
    In this test test_user is not owner of test_review_2
    so endpoints should return 404 for someone who is not the owner.
    """
    client = APIClient()
    client.force_authenticate(test_user)
    body = {"comment": "New comment"}
    response = client.patch(f"/api/user_reviews/{test_review_2.id}/", body)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_ReviewViewSet_patch_changing_restaurant(test_user, test_restaurant, test_review_1, test_restaurant_1):
    """
    User cannot change the restaurant of the review.
    """
    client = APIClient()
    client.force_authenticate(test_user)
    body = {
        "restaurant": test_restaurant_1.id,
    }
    response = client.patch(f"/api/user_reviews/{test_review_1.id}/", body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_ReviewViewSet_patch_requires_authentication():
    client = APIClient()
    response = client.patch("/api/user_reviews/", {})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test delete api/user_reviews/
def test_ReviewViewSet_delete_review_owner(test_user, test_restaurant, test_review_1):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.delete(f"/api/user_reviews/{test_review_1.id}/")
    assert not Review.objects.filter(id=test_review_1.id).exists()
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_ReviewViewSet_delete_restaurant_owner(test_restaurant, test_review_1):
    """
    Owner of the restaurant is also allowed to delete review of his restaurant.
    """
    client = APIClient()
    client.force_authenticate(test_restaurant.owner)
    response = client.delete(f"/api/user_reviews/{test_review_1.id}/")
    assert not Review.objects.filter(id=test_review_1.id).exists()
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_ReviewViewSet_delete_restaurant_manager(test_membership_manager, test_review_1):
    """
    Member of the restaurant with "manager" role is also allowed to delete review of his restaurant.
    """
    client = APIClient()
    client.force_authenticate(test_membership_manager.user)
    response = client.delete(f"/api/user_reviews/{test_review_1.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_ReviewViewSet_delete_review_not_owner_or_membership_restaurant(test_user_1, test_review_1):
    """
    test_user_1 is not owner of test_review_1 is also not owner of the restaurant that this review is about,
    and is not also a manager in this restaurant.So endpoint should return 403.
    """
    client = APIClient()
    client.force_authenticate(test_user_1)
    response = client.delete(f"/api/user_reviews/{test_review_1.id}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_ReviewViewSet_delete_requires_authentication(test_review_1):
    client = APIClient()
    response = client.delete(f"/api/user_reviews/{test_review_1.id}/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
