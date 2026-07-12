from datetime import datetime, time

from booking_system.models import Booking


def test_save_method_in_booking_model(test_restaurant, test_user, test_restaurant_table):
    """
    In this test we create a Booking object with start_time = 17:00:00 and we except that
    fild "end_time" will be automatically set in save method to 18:30:00 because
    test_restaurant.reservation_duration_minutes = 90 minutes.
    """
    booking = Booking.objects.create(
        restaurant=test_restaurant,
        table=test_restaurant_table,
        user=test_user,
        date=datetime.today(),
        start_time=time(17, 0, 0),
    )

    booking.refresh_from_db()
    assert booking.end_time == time(18, 30, 0)
