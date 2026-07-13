"""Transactional email adapter tests."""

from email.message import EmailMessage

import pytest
from pydantic import SecretStr

from nextfight.core.config import Settings
from nextfight.infrastructure.email.smtp import SmtpEmailSender


class CapturingEmailSender(SmtpEmailSender):
    """Capture the fully assembled message without opening an external socket."""

    def __init__(self, settings: Settings) -> None:
        """Initialize an empty message capture."""
        super().__init__(settings)
        self.message: EmailMessage | None = None

    def _send(self, message: EmailMessage) -> None:
        self.message = message


@pytest.mark.asyncio
async def test_password_reset_email_contains_encoded_link() -> None:
    """Build a valid reset email from typed SMTP configuration."""
    sender = CapturingEmailSender(
        Settings(
            smtp_host="smtp.example.com",
            smtp_username="nextfight",
            smtp_password=SecretStr("email-secret"),
            smtp_from_email="support@nextfight.app",
            password_reset_url="https://nextfight.app/reset?source=email",  # noqa: S106
        )
    )

    await sender.send_password_reset("fighter@example.com", "token/value")

    assert sender.configured
    assert sender.message is not None
    assert sender.message["To"] == "fighter@example.com"
    assert "source=email&token=token%2Fvalue" in sender.message.get_content()
