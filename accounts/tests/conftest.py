import pytest

from accounts.models import CustomUser, VerificationCode


@pytest.fixture(autouse=True)
def celery_eager(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


@pytest.fixture
def test_user(db):
    return CustomUser.objects.create_user(email="test@test.com", password="Test_password")


@pytest.fixture
def test_verification_code(db):
    return VerificationCode.objects.create(email="testemail@wp.com", code="123456")
