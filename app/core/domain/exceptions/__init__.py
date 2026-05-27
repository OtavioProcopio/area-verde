from typing import Any, Optional


class ApplicationError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[list[dict[str, Any]]] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(ApplicationError):
    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=404)


class ConflictError(ApplicationError):
    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=409)
