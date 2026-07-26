from datetime import datetime, time, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from rest_framework.exceptions import NotFound

from accounts.models import CustomUser
from booking_system.models import Booking
from booking_system.services import searching_first_available_table
from restaurants.models import Restaurant, RestaurantBan


def get_available_hours_per_day(restaurant: Restaurant, date: str, guests: int) -> list[str]:
    """
    Returns a list with all available hours on the provided date.

    This function take all hours on the provided date according to field "reservation_interval_minutes" and all
    available rules at that day in the restaurant and returns all free time slots at that day.
    """

    if not restaurant or not date or not guests:
        raise ValueError("Fields (restaurant, date, guests) are required")

    # Convert date to datetime object
    try:
        date_object = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date")

    # Take all hours at provided date and validate them
    day_start = datetime.combine(
        date_object,
        time(
            0,
            0,
            0,
        ),
    )
    day_end = datetime.combine(
        date_object,
        time(
            23,
            59,
            59,
        ),
    )
    reservation_interval_minutes = restaurant.reservation_interval_minutes

    # Start checking from 00:00:00 because the restaurant may be open from midnight.
    current_time = day_start

    all_available_hours = []

    while current_time <= day_end:
        try:
            searching_first_available_table(
                restaurant=restaurant,
                date=date_object,
                start_time=current_time.time(),
                guests=guests,
            )

            all_available_hours.append(current_time.strftime("%H:%M"))

        # If validation fails, this time slot is not available
        except ValueError:
            pass
        current_time += timedelta(minutes=reservation_interval_minutes)

    return all_available_hours


def get_all_bookings_per_day(restaurant: Restaurant, date: str) -> QuerySet[Booking]:
    """
    Returns all bookings at provided date with status confirmed, completed or no_show sorted by start_time
    """
    if not restaurant or not date:
        raise ValueError("Fields (restaurant, date) are required")

    try:
        date_object = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format")
    all_bookings = Booking.objects.filter(
        restaurant=restaurant,
        date=date_object,
        status__in=[
            Booking.Status.CONFIRMED,
            Booking.Status.COMPLETED,
            Booking.Status.NO_SHOW,
        ],
    ).order_by("start_time")
    return all_bookings


def create_restaurant_ban(restaurant: Restaurant, email: str, description=None) -> None:
    if not email:
        raise ValueError("Email is required")
    try:
        user = CustomUser.objects.get(email=email)
    except ObjectDoesNotExist:
        raise NotFound("User with provided email does not exist")

    RestaurantBan.objects.create(
        restaurant=restaurant,
        user=user,
        description=description,
    )


def unban_user(restaurant: Restaurant, email: str) -> None:
    """
    Deletes RestaurantBan object with given user if it exists.
    """
    if not email:
        raise ValueError("Email is required")
    try:
        user = CustomUser.objects.get(email=email)
    except ObjectDoesNotExist:
        raise NotFound("User with provided email does not exist")

    try:
        user_ban = RestaurantBan.objects.get(user=user, restaurant=restaurant)
        user_ban.delete()
    except ObjectDoesNotExist:
        raise NotFound("Provided user does not have ban in the restaurant")


def show_all_bans(restaurant: Restaurant, ordering=str) -> QuerySet[RestaurantBan]:
    """
    Returns list of all bans at provided restaurant.
    User can also provide filed "ordering" (default = "created_at", allowed = "created_at", "-created_at"
    """
    if ordering not in ["created_at", "-created_at"]:
        raise ValueError("Invalid ordering")

    all_bans = RestaurantBan.objects.filter(restaurant=restaurant).order_by(f"{ordering}")
    return all_bans


def check_if_user_is_banned(restaurant: Restaurant, email: str) -> RestaurantBan:
    """
    Returns RestaurantBan object with given user if it exists.
    """
    if not email:
        raise ValueError("Email is required")
    try:
        user = CustomUser.objects.get(email=email)
    except ObjectDoesNotExist:
        raise NotFound("User with provided email does not exist")
    try:
        user_ban = RestaurantBan.objects.get(user=user, restaurant=restaurant)
    except ObjectDoesNotExist:
        raise NotFound("Provided user does not have ban in the restaurant")
    return user_ban
