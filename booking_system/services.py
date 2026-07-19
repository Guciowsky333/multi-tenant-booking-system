from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.exceptions import NotFound

from accounts.models import CustomUser
from available_rules.models import AvailableRule, RestaurantBreak, RestaurantException, RestaurantTable
from booking_system.models import Booking
from restaurants.models import Restaurant, RestaurantBan


def create_booking(
    restaurant: Restaurant, date: datetime.date, start_time: datetime.time, guests: int, user: CustomUser
) -> Booking:
    """
    Finds available table and create booking object with it.

    In this function we use transaction.atomic() with select_for_update() in tables to prevent case
    when to user would book the same table at the same time.
    """
    with transaction.atomic():
        # Chacking if user has been banned in this restaurant
        restaurant_ban = RestaurantBan.objects.filter(restaurant=restaurant, user=user).first()
        if restaurant_ban:
            raise ValueError(f"You have been banned in this restaurant.reason: {restaurant_ban.description}")
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

        if booking.status != booking.Status.PENDING:
            raise ValueError("Booking status must be PENDING")

        booking.status = Booking.Status.CONFIRMED
        booking.save()
        return True


def change_booking_status_to_completed(booking: Booking) -> bool:
    """
    Changes booking status to COMPLETED only if it was confirmed first.
    """
    # You cant changes status of the booking to completed if it was not happen yet
    if datetime.today() < datetime.combine(booking.date, booking.start_time):
        raise ValueError("The booking hasn't taken place yet.")

    if booking.status != booking.Status.CONFIRMED:
        raise ValueError("Booking status must be CONFIRMED")

    booking.status = Booking.Status.COMPLETED
    booking.save()
    return True


def change_booking_status_to_cancelled(booking: Booking, user: CustomUser) -> bool:
    """
    Change booking status to CANCELLED only if it was confirmed first.
    User who is the owner of the restaurant can change it only 2 days before the booking date.
    User who is the member of the restaurant on which the booking belongs can change it at any time.
    """

    if booking.status != booking.Status.CONFIRMED:
        raise ValueError("Booking status must be CONFIRMED")

    if booking.user == user:
        today = datetime.today()
        booking_date = datetime.combine(booking.date, booking.start_time)
        if today > (booking_date - timedelta(days=2)):
            raise ValueError(
                "Too late you can change the status of your booking to 'cancelled' at least 2 days before the booking date"
            )

    # If user is not owner of booking he has to be member of the restaurant check "IsMemberOfRestaurantOrOwnerOfBooking" permission
    booking.status = Booking.Status.CANCELLED
    booking.save()
    return True


def change_booking_status_to_no_show(booking: Booking) -> bool:
    """
    This function changes booking status to NO_SHOW only if it was CONFIRMED first, and check
    field "no_show_ban_threshold" in restaurant associated with the booking if user exceeded it Bans this user in this restaurant.
    If field "no_show_ban_threshold" is empty because it is not required field just changes status.
    """
    if booking.status != booking.Status.CONFIRMED:
        raise ValueError("Booking status must be CONFIRMED")
    if datetime.today() < datetime.combine(booking.date, booking.start_time):
        raise ValueError("The booking hasn't taken place yet.")

    no_show_ban_threshold = booking.restaurant.no_show_ban_threshold
    booking.status = Booking.Status.NO_SHOW
    booking.save()
    # If restaurant do not have fild "no_show_ban_threshold" we just change status to "no_show" without checking if user does not exceed it
    if not no_show_ban_threshold:
        return True

    user = booking.user
    restaurant = booking.restaurant
    user_bookings_status_no_show = Booking.objects.filter(restaurant=restaurant, user=user, status="no_show").count()
    if user_bookings_status_no_show >= no_show_ban_threshold:
        # Ban user in the restaurant
        RestaurantBan.objects.get_or_create(
            restaurant=restaurant, user=user, description="The user failed to show up for their booking too many times."
        )
    return True
