from celery import shared_task
from django.core.mail import send_mail
from django.db import transaction

from booking_system.models import Booking


@shared_task
def send_booking_confirmation_email(user_email: str, token: str) -> None:
    send_mail(
        subject="Confirm your restaurant booking",
        message=f"""
        Your booking has been created 
        
        Please click the link below to confirm your booking
        http://localhost:8000/api/bookings/change_status_confirmed/?token={token}
        
        This link is valid for 30 minutes.
        """,
        from_email="bookingsystem@wp.com",
        recipient_list=[user_email],
    )


@shared_task
def cancelled_booking_after_30_minutes(booking_id: int) -> None:
    """
    If after 30 minutes booking object is still Pending (Means that user does not confirm it on email)
    Its changes status to "cancelled".
    """
    with transaction.atomic():
        booking = Booking.objects.select_for_update().filter(id=booking_id).first()
        if not booking:
            return "Booking not found"
        if booking.status != booking.Status.PENDING:
            return "Booking is not pending anymore"
        booking.status = booking.Status.CANCELLED
        booking.save()
        return None
