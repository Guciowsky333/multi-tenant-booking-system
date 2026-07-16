from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.exceptions import NotFound

from accounts.models import CustomUser
from available_rules.models import AvailableRule, RestaurantBreak, RestaurantException, RestaurantTable
from booking_system.models import Booking
from restaurants.models import Restaurant


def create_booking(
    restaurant: Restaurant, date: datetime.date, start_time: datetime.time, guests: int, user: CustomUser
) -> Booking:
    """
    Finds available table and create booking object with it.

    In this function we use transaction.atomic() with select_for_update() in tables to prevent case
    when to user would book the same table at the same time.
    """
    with transaction.atomic():
        table = searching_first_available_table(restaurant, date, start_time, guests)
        booking = Booking.objects.create(
            restaurant=restaurant,
            table=table,
            user=user,
            date=date,
            start_time=start_time,
        )
    return booking


def searching_first_available_table(
    restaurant: Restaurant, date: datetime.date, start_time: datetime.time, guests: int
) -> RestaurantTable:
    """
    Returns RestaurantTable if all conditions will pass
    """

    # +1 because in model AvailableRule we keep days form 1 to 7 not form 0 to 6
    day_of_week = date.weekday() + 1
    rules = AvailableRule.objects.filter(restaurant=restaurant, day_of_week=day_of_week).first()
    if not rules:
        raise ValueError("Restaurant is not open on provided day")
    restaurant_opening_time = rules.opening_time
    restaurant_closing_time = rules.closing_time

    # Firs check if in that day there are any exceptions (Restaurants can have only 1 exception per day)
    exception = RestaurantException.objects.filter(restaurant=restaurant, date=date).first()
    if exception:
        if exception.type == RestaurantException.Type.CLOSED:
            raise ValueError("In provided date restaurant is closed")
        # If type is not closed it is special_hours so we take new opening and closing time
        restaurant_opening_time = exception.opening_time
        restaurant_closing_time = exception.closing_time

    # Set end_time for that booking
    booking_end_time_date = datetime.combine(date, start_time) + timedelta(
        minutes=restaurant.reservation_duration_minutes
    )
    booking_end_time = booking_end_time_date.time()

    if (
        start_time > restaurant_closing_time
        or start_time < restaurant_opening_time
        or booking_end_time > restaurant_closing_time
    ):
        raise ValueError("At provided time restaurant is not open")

    # Each restaurant has a `reservation_interval_minutes` field, and the `start_time` must be consistent with this field.
    booking_start_datetime = datetime.combine(date, start_time)
    restaurant_opening_datetime = datetime.combine(date, restaurant_opening_time)
    minutes_since_opening = (booking_start_datetime - restaurant_opening_datetime).total_seconds() // 60
    if minutes_since_opening % restaurant.reservation_interval_minutes != 0:
        raise ValueError(
            f"Invalid start time. Bookings in this restaurant can only start every "
            f"{restaurant.reservation_interval_minutes} minutes from opening time."
        )

    # Checking if start_time does not overlap breaks at that day
    all_breaks = RestaurantBreak.objects.filter(restaurant=restaurant, day_of_week=day_of_week).all()
    for restaurant_break in all_breaks:
        if booking_end_time > restaurant_break.start and start_time < restaurant_break.end:
            raise ValueError("At provided time the restaurant has break")

    # Checking if any booking does not exist in provided time and date
    all_matching_tables = (
        RestaurantTable.objects.select_for_update().filter(restaurant=restaurant, seats__gte=guests).all()
    )
    allowed_table = None
    for table in all_matching_tables:
        if Booking.objects.filter(
            restaurant=restaurant,
            date=date,
            table=table,
            status__in=["PENDING", "CONFIRMED"],
            start_time__lt=booking_end_time,
            end_time__gt=start_time,
        ).exists():
            continue
        allowed_table = table
        break

    if not allowed_table:
        raise ValueError("No free tables available at provided time and date")
    return allowed_table


def change_booking_status_to_confirmed(token: str) -> bool:
    """
    Returns True if booking exist and its status is PENDING and changes its status to CONFIRMED.
    """
    with transaction.atomic():
        try:
            booking = Booking.objects.select_for_update().filter(confirmation_token=token).first()
        except ValidationError:
            raise ValueError("Invalid token")

        if not booking:
            raise NotFound("Booking not found")
        if booking.status == Booking.Status.CONFIRMED:
            raise ValueError("Booking is already confirmed")

        if booking.status == Booking.Status.CANCELLED:
            raise ValueError("Booking has been cancelled you can not change its status")

        if booking.status == Booking.Status.COMPLETED:
            raise ValueError("Booking has been already completed")
        if booking.status == Booking.Status.PENDING:
            booking.status = Booking.Status.CONFIRMED
            booking.save()
        return True
