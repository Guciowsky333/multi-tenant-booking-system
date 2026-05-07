from rest_framework import serializers


def validate_password_strength(password: str) -> None:
    """
    Check if specified password has at least 8 characters and at least one
    capital letter.
    """

    if len(password) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters")

    if not any(x.isupper() for x in password):
        raise serializers.ValidationError("Password must contain at least one uppercase letter")


def validate_passwords(password: str, password_2: str) -> None:
    validate_password_strength(password)

    if password != password_2:
        raise serializers.ValidationError("Passwords must match")
