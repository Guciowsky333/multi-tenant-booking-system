import secrets
import string


def generate_verification_code() -> str:
    numbers_and_characters = string.digits + string.ascii_letters.upper()
    code = "".join(secrets.choice(numbers_and_characters) for _ in range(6))
    return code
