"""Tests for the email sender interface and console adapter (A1.8)."""


def test_console_sender_records_the_message_in_outbox():
    """A1.8: send() stores to, subject and body in the outbox."""
    from app.adapters.email import ConsoleEmailSender

    sender = ConsoleEmailSender()

    sender.send("ada@example.com", "Welcome", "Your link is ready.")

    assert sender.outbox == [
        {"to": "ada@example.com", "subject": "Welcome", "body": "Your link is ready."}
    ]


def test_console_sender_keeps_messages_in_order():
    """A1.8: each send() adds one entry, in the order the emails were sent."""
    from app.adapters.email import ConsoleEmailSender

    sender = ConsoleEmailSender()

    sender.send("first@example.com", "One", "body one")
    sender.send("second@example.com", "Two", "body two")

    assert [item["to"] for item in sender.outbox] == [
        "first@example.com",
        "second@example.com",
    ]


def test_console_sender_prints_body_to_terminal(capsys):
    """A1.8: the email body appears in the terminal so a developer can copy the link."""
    from app.adapters.email import ConsoleEmailSender

    sender = ConsoleEmailSender()

    sender.send("ada@example.com", "Welcome", "https://example.test/invite/abc123")

    assert "https://example.test/invite/abc123" in capsys.readouterr().out


def test_get_email_sender_returns_an_object_with_send():
    """A1.8: the get_email_sender dependency returns a sender that has a send method."""
    from app.adapters.email import get_email_sender

    sender = get_email_sender()

    assert callable(getattr(sender, "send", None))
