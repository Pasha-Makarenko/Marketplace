from dataclasses import dataclass

from marketplace.domain.exceptions import DomainError


@dataclass(frozen=True)
class Identity:
    _value: int | None

    @property
    def value(self) -> int:
        if not self._value:
            raise DomainError("The identity has not been set.")
        return self._value

    def __composite_values__(self) -> tuple[int | None]:
        return (self._value,)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identity):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
