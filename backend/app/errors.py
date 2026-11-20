"""One error type that services raise. main.py turns it into a JSON response with a status code."""


class DomainError(Exception):
    """A rule was broken (wrong password, expired link, limit reached). Carries the HTTP status and message."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
