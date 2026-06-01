import pytest
from rest_framework import status
from rest_framework.test import APIClient

from memberships.models import MemberShip

# Test for /api/memberships/


# Post method
def test_MemberShipViewSet_post(test_owner, test_restaurant, test_user):
    client = APIClient()
    client.force_authenticate(test_owner)

    body = {"restaurant": test_restaurant.id, "email": test_user.email, "role": "staff"}
    response = client.post("/api/memberships/", body)
    assert response.status_code == status.HTTP_201_CREATED
    assert MemberShip.objects.filter(restaurant=test_restaurant.id, user=test_user.id).exists()


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # restaurant id =1 is test_restaurant
        # Missing restaurant
        ({"restaurant": "", "email": "test@test1.com", "role": "staff"}, status.HTTP_400_BAD_REQUEST),
        # Missing email
        ({"restaurant": 1, "email": "", "role": "staff"}, status.HTTP_400_BAD_REQUEST),
        # Missing role
        ({"restaurant": 1, "email": "test@test1.com", "role": ""}, status.HTTP_400_BAD_REQUEST),
        # User with provided email does not exist
        ({"restaurant": 1, "email": "NotExist@email.com", "role": "staff"}, status.HTTP_400_BAD_REQUEST),
        # Wrong format email
        ({"restaurant": 1, "email": "wrong_format", "role": "staff"}, status.HTTP_400_BAD_REQUEST),
        # Wron role allowed (staff, manager)
        ({"restaurant": 1, "email": "test@test1.com", "role": "wrong_role"}, status.HTTP_400_BAD_REQUEST),
    ],
)
def test_MemberShipViewSet_post_invalid_data(payload, expected_status, test_owner, test_restaurant, test_user):
    client = APIClient()
    client.force_authenticate(test_owner)

    response = client.post("/api/memberships/", payload)
    assert response.status_code == expected_status


def test_MemberShipViewSet_post_owner_cannot_be_member(test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)
    body = {"restaurant": test_restaurant.id, "email": test_owner.email, "role": "staff"}
    response = client.post("/api/memberships/", body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_MemberShipViewSet_post_not_owner(test_user, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_user)
    body = {"restaurant": test_restaurant.id, "email": test_user.email, "role": "staff"}
    response = client.post("/api/memberships/", body)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_MemberShipViewSet_post_unique_user(test_owner, test_membership):
    """
    Each user can have only one membership model with one restaurant.In this test
    we try creates another membership model with the same user, like in test_membership
    and with the same restaurant.Endpoint should return error 400
    """
    client = APIClient()
    client.force_authenticate(test_owner)
    body = {
        "restaurant": test_membership.restaurant.id,
        "email": test_membership.user.email,
        "role": "manager",
    }
    response = client.post("/api/memberships/", body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_MemberShipViewSet_post_requires_authentication():
    client = APIClient()
    response = client.post("/api/memberships/", {})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Get method
def test_MemberShipViewSet_get_owner(test_owner, test_restaurant, test_user, test_user_1):
    """
    In this test we create 2 members of test_restaurant and check whether
    our endpoint correctly show all members to owner of test_restaurant.
    """

    MemberShip.objects.create(restaurant=test_restaurant, user=test_user, role="staff")
    MemberShip.objects.create(restaurant=test_restaurant, user=test_user_1, role="staff")

    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get(f"/api/memberships/?restaurant_id={test_restaurant.id}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


def test_MemberShipViewSet_get_member(test_membership, test_user_1, test_restaurant):
    """
    In this test we create 1 member and take test_membership from fixture and check
    whether our endpoint correctly show all members to member of test_restaurant.
    """
    client = APIClient()
    client.force_authenticate(test_membership.user)

    MemberShip.objects.create(restaurant=test_restaurant, user=test_user_1, role="staff")

    response = client.get(f"/api/memberships/?restaurant_id={test_restaurant.id}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


def test_MemberShipViewSet_get_not_member_or_owner(test_user_1, test_restaurant):
    """
    In this test we check whether test_user_1 who is not member or owner of test_restaurant has access
    to our endpoint.
    """
    client = APIClient()
    client.force_authenticate(test_user_1)
    response = client.get(f"/api/memberships/?restaurant_id={test_restaurant.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_MemberShipViewSet_get_not_specified_restaurant_id(test_owner, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.get("/api/memberships/?restaurant_id=")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_MemberShipViewSet_get_requires_authentication():
    client = APIClient()
    response = client.get("/api/memberships/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Put method
def test_MemberShipViewSet_put(test_owner, test_membership):
    client = APIClient()
    client.force_authenticate(test_owner)

    # Changes role from staff to manager for test_membership
    body = {"role": "manager"}
    response = client.put(f"/api/memberships/{test_membership.id}/", body)
    test_membership.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert test_membership.role == "manager"


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Missing role
        ({"role": ""}, status.HTTP_400_BAD_REQUEST),
        # Wrong role allowed (staff, manager)
        ({"role": "wrong_role"}, status.HTTP_400_BAD_REQUEST),
    ],
)
def test_MemberShipViewSet_put_invalid_data(payload, expected_status, test_owner, test_membership, test_restaurant):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.put(f"/api/memberships/{test_membership.id}/", payload)
    assert response.status_code == expected_status


def test_MemberShipViewSet_put_returns_403_for_not_owner(test_user_1, test_membership):
    client = APIClient()
    client.force_authenticate(test_user_1)
    response = client.put(f"/api/memberships/{test_membership.id}/", {})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_MemberShipViewSet_put_requires_authentication():
    client = APIClient()
    response = client.put("/api/memberships/", {})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Patch method
def test_MemberShipViewSet_patch(test_owner, test_membership):
    client = APIClient()
    client.force_authenticate(test_owner)
    body = {"role": "staff"}
    response = client.patch(f"/api/memberships/{test_membership.id}/", body)
    assert response.status_code == status.HTTP_200_OK


def test_MemberShipViewSet_patch_returns_403_for_not_owner(test_user_1, test_membership):
    client = APIClient()
    client.force_authenticate(test_user_1)
    response = client.patch(f"/api/memberships/{test_membership.id}/", {})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_MemberShipViewSet_patch_requires_authentication():
    client = APIClient()
    response = client.patch("/api/memberships/", {})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Delete method
def test_MemberShipViewSet_delete(test_owner, test_membership):
    client = APIClient()
    client.force_authenticate(test_owner)
    response = client.delete(f"/api/memberships/{test_membership.id}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not MemberShip.objects.filter(id=test_membership.id).exists()


def test_MemberShipViewSet_delete_not_owner(test_user_1, test_membership):
    client = APIClient()
    client.force_authenticate(test_user_1)
    response = client.delete(f"/api/memberships/{test_membership.id}/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_MemberShipViewSet_delete_requires_authentication():
    client = APIClient()
    response = client.delete("/api/memberships/", {})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
