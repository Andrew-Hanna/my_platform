"""Email sending behind an interface. Dev uses the console adapter; a real provider replaces it later."""

from typing import Protocol


class EmailSender(Protocol):
    """Anything that can send an email."""

    def send(self, to: str, subject: str, body: str) -> None: ...


class ConsoleEmailSender:
    """Prints emails to the terminal and keeps them in an outbox list (used by tests and in dev)."""

    def __init__(self) -> None:
        self.outbox: list[dict[str, str]] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.outbox.append({"to": to, "subject": subject, "body": body})
        print(f"--- email to {to}: {subject}\n{body}")


_default_sender = ConsoleEmailSender()


def get_email_sender() -> EmailSender:
    """FastAPI dependency that returns the sender for this process. Tests replace it with an override."""
    return _default_sender
