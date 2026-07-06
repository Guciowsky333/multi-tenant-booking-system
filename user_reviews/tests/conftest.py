import pytest

from user_reviews.models import Review


@pytest.fixture
def test_review_1(db, test_restaurant, test_user):
    return Review.objects.create(
        user=test_user,
        restaurant=test_restaurant,
        rating=8,
        comment="Test comment",
    )


@pytest.fixture
def test_review_2(db, test_restaurant, test_user_1):
    return Review.objects.create(
        user=test_user_1,
        restaurant=test_restaurant,
        rating=7,
        comment="Test comment",
    )
