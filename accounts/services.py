from django.db import transaction

from accounts.models import CustomUser, VerificationCode
from accounts.tasks import delete_verification_code, send_verification_email


def create_verification_code(email: str) -> None:
    """
    Creates a VerificationCode model with specified email, generates code and sends this code to this email

    Important : This code will be valid only for 15 minutes after this time VerificationCode model
    with this code and email will be deleted.
    """

    # The VerificationCode model automatically generates a unique code
    verify_code = VerificationCode.objects.create(
        email=email,
    )

    # Send mail
    send_verification_email.delay(email, verify_code.code)
    # Delete the VerificationCode model after 15 minutes
    delete_verification_code.apply_async(args=[verify_code.id], countdown=900)


def create_account(password: str, email: str, code: str) -> None:
    """
    Checks if provided code is valid and if yes creates a new account
    """
    verify_code = VerificationCode.objects.filter(email=email, code=code).first()
    if not verify_code:
        raise ValueError("Invalid email or code")

    with transaction.atomic():
        CustomUser.objects.create_user(email=email, password=password)
        verify_code.delete()


def change_password(old_password: str, new_password: str, user: CustomUser) -> None:
    """
    Check if old password belong to specified user and change this password to a new password
    """

    if not user.check_password(old_password):
        raise ValueError("old password must belong to user")

    user.set_password(new_password)
    user.save()
