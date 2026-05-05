from accounts.models import CustomUser


def create_account(email: str, password: str) -> None:
    """
    Create new user account with given email and password
    """
    CustomUser.objects.create_user(email=email, password=password)
