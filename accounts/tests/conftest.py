import pytest

from accounts.models import CustomUser, VerificationCode


@pytest.fixture
def test_user(db):
    return CustomUser.objects.create_user(email="test@test.com", password="Test_password")


@pytest.fixture
def test_verification_code(db):
    return VerificationCode.objects.create(email="testemail@wp.com", code="123456")
