import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser, VerificationCode


# Test for /api/accounts/send_verification_email/
@pytest.mark.django_db
def test_SendVerificationEmailView():
    """
    In this test we check whether our endpoint correctly creates a VerificationCode model
    with provided email.
    """
    client = APIClient()
    body = {"email": "testemail@wp.com", "password": "Test_password", "password_2": "Test_password"}

    response = client.post("/api/accounts/send_verification_email/", body)
    assert response.status_code == status.HTTP_201_CREATED
    assert VerificationCode.objects.filter(email=body["email"]).exists()


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Invalid email
        (
            {"email": "wrong_email", "password": "Test_password", "password_2": "Test_password"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # Account with this email already exist
        (
            {"email": "test@test.com", "password": "Test_password", "password_2": "Test_password"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # Password does not have at least one capital letter
        (
            {"email": "test_email@.com", "password": "test_password", "password_2": "test_password"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # Password is too short (at least 8 characters)
        ({"email": "test_email@.com", "password": "Test", "password_2": "Test"}, status.HTTP_400_BAD_REQUEST),
        # Passwords are not the same
        (
            {"email": "test_email@.com", "password": "Test_password_1", "password_2": "Test_password_2"},
            status.HTTP_400_BAD_REQUEST,
        ),
    ],
)
def test_SendVerificationEmailView_invalid_payload(payload, expected_status, test_user):
    """
    In this test we check all possible invalid payloads
    """
    client = APIClient()
    response = client.post("/api/accounts/send_verification_email/", payload)
    assert response.status_code == expected_status


# Test for /api/accounts/create/
@pytest.mark.django_db
def test_CreateAccountAPIView(test_verification_code):
    """
    In this test we create a VerificationCode model with provided email.
    And we check if our endpoint correctly checks if provided code is valid and creates new account.
    """
    client = APIClient()
    body = {"email": "testemail@wp.com", "password": "Test_password", "password_2": "Test_password", "code": "123456"}

    response = client.post("/api/accounts/create/", body)
    assert response.status_code == status.HTTP_201_CREATED

    created_user = CustomUser.objects.filter(email=body["email"]).first()
    assert created_user
    assert created_user.email == body["email"]
    assert created_user.check_password(body["password"])


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Wrong email form
        (
            {"email": "wrong_email", "password": "Test_password", "password_2": "Test_password", "code": "123456"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # To short password (at least 8 characters)
        (
            {"email": "testemail@wp.com", "password": "Test", "password_2": "Test", "code": "123456"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # Missing capital letter in the password
        (
            {"email": "testemail@wp.com", "password": "test_password", "password_2": "test_password", "code": "123456"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # Password and password_2 are not the same
        (
            {
                "email": "testemail@wp.com",
                "password": "Test_password1",
                "password_2": "Test_password2",
                "code": "123456",
            },
            status.HTTP_400_BAD_REQUEST,
        ),
        # User with this email already exist
        (
            {"email": "test@test.com", "password": "Test_password", "password_2": "Test_password", "code": "123456"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # Invalid code
        (
            {"email": "testemail@wp.com", "password": "Test_password", "password_2": "Test_password", "code": "654321"},
            status.HTTP_400_BAD_REQUEST,
        ),
    ],
)
def test_CreateAccountAPIView_invalid_payload(payload, expected_status, test_user, test_verification_code):

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


#  Test for /api/accounts/send_reset_password_code/
def test_SendResetPasswordCodeAPIView(test_user):
    """
    In this test we check whether our endpoint correctly create VerificationCode
    assigned to provided user's email
    """
    client = APIClient()

    body = {
        "email": f"{test_user.email}",
    }

    response = client.post("/api/accounts/send_reset_password_code/", body)
    assert response.status_code == status.HTTP_201_CREATED
    assert VerificationCode.objects.filter(email=body["email"]).exists()


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # Empty email
        ({"email": ""}, status.HTTP_400_BAD_REQUEST),
        # Incorrect email format
        ({"email": "wrong_format"}, status.HTTP_400_BAD_REQUEST),
        # User with provided email does not exist
        ({"email": "testemail@wp.com"}, status.HTTP_404_NOT_FOUND),
    ],
)
@pytest.mark.django_db
def test_SendResetPasswordCodeAPIView_invalid_payload(payload, expected_status):
    client = APIClient()

    response = client.post("/api/accounts/send_reset_password_code/", payload)
    assert response.status_code == expected_status


# Test for /api/accounts/reset_password/
def test_ResetPasswordAPIView(test_user):
    """
    In this test we create a VerificationCode model assigned to provided user's email
    and check whether if provide code is valid this endpoint correctly reset user's password to a new one
    """
    verification_code = VerificationCode.objects.create(email=test_user.email)
    client = APIClient()

    body = {
        "email": f"{test_user.email}",
        "new_password": "NewPassword",
        "new_password_2": "NewPassword",
        "code": f"{verification_code.code}",
    }

    response = client.post("/api/accounts/reset_password/", body)
    test_user.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert test_user.check_password(body["new_password"])

    # If everything is correct endpoint also should delete VerificationCode
    assert not VerificationCode.objects.filter(email=body["email"], code=body["code"]).exists()


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # User with provided email does not exist
        (
            {
                "email": "testemail@wp.com",
                "new_password": "NewPassword",
                "new_password_2": "NewPassword",
                "code": "123456",
            },
            status.HTTP_404_NOT_FOUND,
        ),
        # Too short new password (at least 8 characters)
        (
            {"email": "test@test.com", "new_password": "New", "new_password_2": "New", "code": "123456"},
            status.HTTP_400_BAD_REQUEST,
        ),
        # New password must contain at least one uppercase letter
        (
            {
                "email": "test@test.com",
                "new_password": "newpassword",
                "new_password_2": "newpassword",
                "code": "123456",
            },
            status.HTTP_400_BAD_REQUEST,
        ),
        # Field new_password and new_password_2 are not the same
        (
            {
                "email": "test@test.com",
                "new_password": "Newpassword1",
                "new_password_2": "Newpassword2",
                "code": "123456",
            },
            status.HTTP_400_BAD_REQUEST,
        ),
        # Invalid code
        (
            {
                "email": "test@test.com",
                "new_password": "Newpassword",
                "new_password_2": "Newpassword",
                "code": "654321",
            },
            status.HTTP_400_BAD_REQUEST,
        ),
    ],
)
def test_ResetPasswordAPIView_invalid_payload(payload, expected_status, test_user):
    client = APIClient()
    VerificationCode.objects.create(email=test_user.email, code="123456")
    response = client.post("/api/accounts/reset_password/", payload)
    assert response.status_code == expected_status
