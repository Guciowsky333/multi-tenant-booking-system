import pytest

from booking_system.models import Booking
from booking_system.tasks import cancelled_booking_after_30_minutes


def test_cancelled_booking_after_30_minutes_task(test_booking_1):
    """
    This task change status of provided booking to cancelled if it is still pending.
    """
    cancelled_booking_after_30_minutes(test_booking_1.id)
    test_booking_1.refresh_from_db()
    assert test_booking_1.status == Booking.Status.CANCELLED


@pytest.mark.parametrize(
    "booking_status",
    [
        "confirmed",
        "cancelled",
        "completed",
    ],
)
def test_cancelled_booking_after_30_minutes_task_different_status_than_pending(test_booking_1, booking_status):
    """
    This task is use in post method in "/api/bookings/" and it changes status of provided booking on
    cancelled if it is still pending.If booking have eny different status task do nothing.
    """
    test_booking_1.status = booking_status
    test_booking_1.save()

    cancelled_booking_after_30_minutes(test_booking_1.id)
    test_booking_1.refresh_from_db()
    # After this task status should be still the same
    assert test_booking_1.status == booking_status
