import pytest

from memberships.models import MemberShip


@pytest.fixture
def test_membership(db, test_user, test_restaurant):
    return MemberShip.objects.create(
        restaurant=test_restaurant,
        user=test_user,
        role="staff",
    )
