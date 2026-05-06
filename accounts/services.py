from accounts.models import CustomUser


def create_account(email: str, password: str) -> None:
    """
    Create new user account with given email and password
    """
    CustomUser.objects.create_user(email=email, password=password)


def change_password(old_password: str, new_password: str, user: CustomUser) -> None:
    """
    Check if old password belong to specified user and change this password to a new password
    """

    if not user.check_password(old_password):
        raise ValueError("old password must belong to user")

    user.set_password(new_password)
    user.save()
