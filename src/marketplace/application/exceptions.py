class ApplicationError(Exception):
    pass


class ValidationError(ApplicationError):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or "Validation Error")


class InvalidEmail(ValidationError):
    def __init__(self, email: str) -> None:
        message = f"Email validation error: {email}"
        super().__init__(message)
