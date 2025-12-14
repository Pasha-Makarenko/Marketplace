import re
from typing import Final

from marketplace.application.exceptions import InvalidEmail, ValidationError

PATTERN: Final[re.Pattern[str]] = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

EMAIL_LENGTH: Final[int] = 320


def validate_length(
    *,
    value: str,
    field_name: str,
    max_length: int,
    min_length: int | None = None,
) -> None:
    if min_length is not None and len(value) < min_length:
        raise ValidationError(
            message=f"{field_name} must be at least {min_length} characters"
        )

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


PHONE_PATTERN: Final[re.Pattern[str]] = re.compile(r"^\\+?[0-9]{8,20}$")


def validate_phone(value: str) -> None:
    if not re.match(PHONE_PATTERN, value):
        raise ValidationError(
            "phone must contain 8-20 digits, optional leading +"
        )
