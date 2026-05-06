import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser


# Test for /api/accounts/create/
@pytest.mark.django_db
def test_CreateAccountAPIView():
    """
    In this test we check if user with specified data will be created correctly
    """
    client = APIClient()
    body = {"email": "testemail@wp.com", "password": "Test_password", "password_2": "Test_password"}

    response = client.post("/api/accounts/create/", body)

    assert response.status_code == status.HTTP_201_CREATED
    assert CustomUser.objects.filter(email=body["email"]).exists()


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Wrong email form
        (
            {"email": "wrong_email", "password": "Test_password", "password_2": "Test_password"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # To short password (at least 8 characters)
        ({"email": "testemail@wp.com", "password": "Test", "password_2": "Test"}, status.HTTP_400_BAD_REQUEST),
        # Missing capital letter in the password
        (
            {"email": "testemail@wp.com", "password": "test_password", "password_2": "test_password"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # Password and password_2 are not the same
        (
            {"email": "testemail@wp.com", "password": "Test_password1", "password_2": "Test_password2"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # User with this email already exist
        (
            {"email": "test@test.com", "password": "Test_password", "password_2": "Test_password"},
            status.HTTP_400_BAD_REQUEST,
        ),
    ],
)
def test_CreateAccountAPIView_invalid_payload(payload, expected_status, test_user):
    client = APIClient()
    response = client.post("/api/accounts/create/", payload)
    assert response.status_code == expected_status


# Test for /api/accounts/logout/
def test_LogoutAPIView(test_user):
    """
    In this test we generate a refresh token for our user and check if endpoint correctly return to
    status cod 200
    """

    client = APIClient()
    client.force_authenticate(user=test_user)

    refresh = RefreshToken.for_user(test_user)
    token = str(refresh)

    response = client.post("/api/accounts/logout/", {"refresh_token": token})

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Without refresh token
        ({"refresh_token": ""}, status.HTTP_400_BAD_REQUEST),
        # Wrong refresh token
        ({"refresh_token": "wrona_refresh_token"}, status.HTTP_400_BAD_REQUEST),
    ],
)
def test_LogoutAPIView_invalid_token(payload, expected_status, test_user):
    client = APIClient()
    client.force_authenticate(user=test_user)
    response = client.post("/api/accounts/logout/", payload)
    assert response.status_code == expected_status


def test_LogoutAPIView_requires_authentication():
    client = APIClient()
    response = client.post("/api/accounts/logout/", {})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test for /api/accounts/change_password/


def test_ChangePasswordAPIView(test_user):
    """
    In this test we check if password of specified user will be changed to a new password correctly
    """
    client = APIClient()
    client.force_authenticate(user=test_user)

    body = {
        # test_user password
        "old_password": "Test_password",
        "new_password": "New_password",
        "new_password_2": "New_password",
    }

    response = client.post("/api/accounts/change_password/", body)
    assert response.status_code == status.HTTP_200_OK
    assert test_user.check_password(body["new_password"])


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Field old_password is empty
        (
            {"old_password": "", "new_password": "New_password", "new_password_2": "New_password"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # Specified old password not belongs to the request user
        (
            {"old_password": "wrong", "new_password": "New_password", "new_password_2": "New_password"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # Fields old_password and new_password are the same
        (
            {"old_password": "Test_password", "new_password": "Test_password", "new_password_2": "Test_password"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # Fields new_password and new_password_2 are not the same
        (
            {"old_password": "Test_password", "new_password": "New_password", "new_password_2": "New_password1"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # New password must contain at least one uppercase letter
        (
            {"old_password": "Test_password", "new_password": "new_password", "new_password_2": "new_password"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # New password is too short
        (
            {"old_password": "Test_password", "new_password": "new", "new_password_2": "new"},
            status.HTTP_400_BAD_REQUEST,
        ),
    ],
)
def test_ChangePasswordAPIView_invalid_payload(payload, expected_status, test_user):
    client = APIClient()
    client.force_authenticate(user=test_user)
    response = client.post("/api/accounts/change_password/", payload)
    assert response.status_code == expected_status


def test_ChangePasswordAPIView_requires_authentication():
    client = APIClient()
    response = client.post("/api/accounts/change_password/", {})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
