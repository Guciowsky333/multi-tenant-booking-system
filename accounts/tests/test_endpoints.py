import pytest
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import CustomUser


@pytest.mark.django_db
class TestCreateAccountAPIView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.url = "/api/accounts/create/"

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
        ],
    )
    def test_invalid_payload(self, payload, expected_status):
        response = self.client.post(self.url, payload)
        assert response.status_code == expected_status
