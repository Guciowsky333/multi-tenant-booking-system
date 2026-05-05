import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser


@pytest.mark.django_db
class TestCreateAccountAPIView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.url = "/api/accounts/create/"

        CustomUser.objects.create(
            email="existingemail@test.com",
            password="Test_password",
        )

    def test_happy_path(self):
        """
        In this test we check if user with specified data will be created correctly
        """

        body = {"email": "testemail@wp.com", "password": "Test_password", "password_2": "Test_password"}

        response = self.client.post(self.url, body)

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
                {"email": "existingemail@test.com", "password": "Test_password", "password_2": "Test_password"},
                status.HTTP_400_BAD_REQUEST,
            ),
        ],
    )
    def test_invalid_payload(self, payload, expected_status):
        response = self.client.post(self.url, payload)
        assert response.status_code == expected_status


@pytest.mark.django_db
class TestLogoutAPIView:
    @pytest.fixture(autouse=True)
    def setup(self, test_user):
        self.client = APIClient()
        self.url = "/api/accounts/logout/"
        self.user = test_user
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh)
        self.client.force_authenticate(user=test_user)

    def test_logout(self):
        response = self.client.post(self.url, {"refresh_token": self.token})
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
    def test_invalid_token(self, payload, expected_status):
        response = self.client.post(self.url, payload)
        assert response.status_code == expected_status

    def test_requires_authentication(self):
        client = APIClient()
        response = client.post(self.url, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
