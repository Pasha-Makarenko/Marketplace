class DomainError(Exception):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Domain Error")


class BaseNotFound(Exception):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message)


class EntityNotFound(BaseNotFound):
    def __init__(self, field_name: str, value: int) -> None:
        message = f"{field_name} with ID {value} not found"
        super().__init__(message)