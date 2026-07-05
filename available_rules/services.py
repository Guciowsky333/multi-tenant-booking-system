from available_rules.models import AvailableRule, RestaurantBreak


def validate_break(restaurant: int, start: str, end: str, day_of_week: int, instance=None) -> bool:
    """
    Returns 400 if break won't pass all validations
    if it did then return True
    """
    rules = AvailableRule.objects.filter(restaurant=restaurant, day_of_week=day_of_week).first()

    # Check if rules with provided day exist with this restaurant
    if not rules:
        raise ValueError("If there are no rules on a given day, a break cannot be added to that day.")

    # Check if the break time matches the restaurant's opening time
    if rules.opening_time > start or rules.closing_time < end:
        raise ValueError("Provided hours of break are out of the opening hours of the restaurant.")

    # Check if the break not overlap with already exists breaks in this restaurant
    all_breaks_in_this_day = RestaurantBreak.objects.filter(restaurant=restaurant, day_of_week=day_of_week).all()

    # Exclude the current instance from the queryset to avoid self-overlap validation
    # during PUT/PATCH requests — we only want to check against other existing breaks.
    if instance:
        all_breaks_in_this_day = all_breaks_in_this_day.exclude(pk=instance.pk)

    for exist_break in all_breaks_in_this_day:
        if exist_break.start < end and start < exist_break.end:
            raise ValueError(
                "You have to change time of this break."
                "This break would be overlap already exist break in this restaurant."
            )

    return True
