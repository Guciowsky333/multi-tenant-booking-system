import pytest
from django.core import mail

from booking_system.models import Booking
from booking_system.tasks import (
    cancelled_booking_after_30_minutes,
    send_booking_confirmation_email,
    send_reminder_email,
)


def test_send_booking_confirmation_email(test_booking_1):
    send_booking_confirmation_email(test_booking_1.user.email, test_booking_1.confirmation_token)
    assert len(mail.outbox) == 1


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
        "no_show",
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


def test_send_reminder_email(test_booking_1):
    """
    In this test we change status of test_booking_1 to CONFIRMED
    so "send_reminder_email" should send email to booking user
    """
    test_booking_1.status = Booking.Status.CONFIRMED
    test_booking_1.save()

    send_reminder_email(test_booking_1.user.email, test_booking_1.id)
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Reservation reminder"


def test_send_reminder_email_booking_not_found(test_booking_1):
    """
    In this test we use 777 id that not exist so we expect that task
    does not send email
    """
    send_reminder_email(test_booking_1.user.email, 777)
    assert len(mail.outbox) == 0


@pytest.mark.parametrize(
    "booking_status",
    [
        "pending",
        "completed",
        "cancelled",
        "no_show",
    ],
)
def test_send_reminder_email_booking_status_not_confirmed(booking_status, test_booking_1):
    """
    In this test test_booking_1 has different status than confirmed so we
    expect that task does not send email
    """
    test_booking_1.status = booking_status
    test_booking_1.save()
    send_reminder_email(test_booking_1.user.email, test_booking_1.id)
    assert len(mail.outbox) == 0
