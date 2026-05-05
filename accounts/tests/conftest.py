import pytest

from accounts.models import CustomUser


@pytest.fixture
def test_user():
    return CustomUser.objects.create(email="test@test.com", password="test_password")
