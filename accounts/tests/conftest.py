import pytest

from accounts.models import CustomUser


@pytest.fixture
def test_user(db):
    return CustomUser.objects.create_user(email="test@test.com", password="Test_password")
