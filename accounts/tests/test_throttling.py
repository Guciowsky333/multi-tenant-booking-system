from rest_framework import status
from rest_framework.test import APIClient


def test_ThrottledTokenObtainPairView(test_user):
    """
    In endpoint ThrottledTokenObtainPairView rate limiting = 5/minute so endpoint should
    return 429 after 5 requests from test_user_3
    """
    client = APIClient()
    body = {"email": test_user.email, "password": "Test_password"}
    for _ in range(5):
        response = client.post("/api/accounts/token/", body)
        assert response.status_code == status.HTTP_200_OK

    # After 5 request we send another request and this time endpoint should return 429

    response = client.post("/api/accounts/token/", body)
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_throttled_anon(test_user_3):
    """
    Every endpoint have set up rate limiting for not authenticated users at 20/minute
    """
    client = APIClient()
    body = {
        "email": test_user_3.email,
    }
    for _ in range(20):
        response = client.post("/api/accounts/send_reset_password_code/", body)
        assert response.status_code == status.HTTP_201_CREATED

    # After 20 request endpoint should return 429 for not authenticated user
    response = client.post("/api/accounts/send_reset_password_code/", body)
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_throttled_user(test_user_3):
    """
    Every endpoint have set up rate limiting for authenticated users at 100/minute
    """
    client = APIClient()
    client.force_authenticate(test_user_3)
    for _ in range(100):
        response = client.get("/api/accounts/me/")
        assert response.status_code == status.HTTP_200_OK

    response = client.get("/api/accounts/me/")
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
