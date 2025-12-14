import re
from dataclasses import dataclass
from typing import Final

from marketplace.domain.exceptions import DomainError

PHONE_PATTERN: Final[re.Pattern[str]] = re.compile(r"^\+?[0-9]{8,20}$")


@dataclass(frozen=True, slots=True)
class Phone:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not PHONE_PATTERN.match(normalized):
            raise DomainError(
                "Phone must contain 8-20 digits; optional leading +"
            )
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
