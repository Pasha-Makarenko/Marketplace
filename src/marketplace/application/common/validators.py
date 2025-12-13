import re
from typing import Final

from marketplace.application.exceptions import InvalidEmail, ValidationError

PATTERN: Final[re.Pattern[str]] = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

EMAIL_LENGTH: Final[int] = 320


def validate_length(max_length: int, field_name: str, value: str) -> None:
    if len(value) > max_length:
        raise ValidationError(
            message=f"{field_name} must be less than {max_length} characters"
        )


def validate_email(value: str) -> None:
    if not re.match(PATTERN, value):
        raise InvalidEmail(value)

    if len(value) > EMAIL_LENGTH:
        raise ValidationError(
            message=f"{value} must be less than {EMAIL_LENGTH} characters"
        )
