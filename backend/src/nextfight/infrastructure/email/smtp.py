"""Secure SMTP adapter for transactional account email."""

import asyncio
import smtplib
from email.message import EmailMessage
from urllib.parse import urlencode

from nextfight.core.config import Settings


class SmtpEmailSender:
    """Deliver transactional email through configured authenticated SMTP."""

    def __init__(self, settings: Settings) -> None:
        """Bind immutable SMTP and public-link configuration."""
        self._settings = settings

    @property
    def configured(self) -> bool:
        """Return whether enough settings exist to authenticate and send."""
        return bool(
            self._settings.smtp_host
            and self._settings.smtp_username
            and self._settings.smtp_password
            and self._settings.smtp_from_email
        )

    async def send_password_reset(self, email: str, token: str) -> None:
        """Send a password reset link without logging or persisting the raw token."""
        if not self.configured:
            return
        query = urlencode({"token": token})
        separator = "&" if "?" in self._settings.password_reset_url else "?"
        link = f"{self._settings.password_reset_url}{separator}{query}"
        message = EmailMessage()
        message["Subject"] = "Reset your NextFight password"
        message["From"] = self._settings.smtp_from_email
        message["To"] = email
        message.set_content(
            "A password reset was requested for your NextFight account.\n\n"
            f"Open this link to choose a new password:\n{link}\n\n"
            "If you did not request this, you can ignore this email."
        )
        await asyncio.to_thread(self._send, message)

    def _send(self, message: EmailMessage) -> None:
        host = self._settings.smtp_host
        username = self._settings.smtp_username
        password = self._settings.smtp_password
        if host is None or username is None or password is None:
            return
        with smtplib.SMTP(host, self._settings.smtp_port, timeout=10) as client:
            client.ehlo()
            if self._settings.smtp_use_tls:
                client.starttls()
                client.ehlo()
            client.login(username, password.get_secret_value())
            client.send_message(message)
