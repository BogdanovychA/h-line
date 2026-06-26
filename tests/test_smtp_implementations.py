# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from email.message import EmailMessage
from unittest.mock import MagicMock, patch

import pytest

from core.smtp_implementations import SMTPSenderSSL, SMTPSenderTLS
from models.email_errors import EmailSendError


class _MockFluent:
    def get(self, key, **kwargs):
        # Return format strings with placeholder names for testing if args present
        if kwargs:
            items = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            return f"{key} ({items})"
        return key


@pytest.fixture
def fluent():
    return _MockFluent()


@pytest.fixture
def sample_message():
    msg = EmailMessage()
    msg["To"] = "recipient@example.com"
    msg["From"] = "sender@example.com"
    msg["Subject"] = "Test Subject"
    msg.set_content("Test body")
    return msg


def test_smtp_sender_ssl_success(fluent, sample_message):
    with patch("core.smtp_implementations.smtplib.SMTP_SSL") as mock_smtp_ssl_class:
        mock_server = MagicMock()
        # Mocking context manager behavior (__enter__ / __exit__)
        mock_smtp_ssl_class.return_value.__enter__.return_value = mock_server

        sender = SMTPSenderSSL(
            server="smtp.example.com",
            port=465,
            email="user@example.com",
            password="secret_password",
            fluent=fluent,
        )

        sender.send(sample_message)

        mock_smtp_ssl_class.assert_called_once_with("smtp.example.com", 465)
        mock_server.login.assert_called_once_with("user@example.com", "secret_password")
        mock_server.send_message.assert_called_once_with(sample_message)


def test_smtp_sender_tls_success(fluent, sample_message):
    with patch("core.smtp_implementations.smtplib.SMTP") as mock_smtp_class:
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server

        sender = SMTPSenderTLS(
            server="smtp.example.com",
            port=587,
            email="user@example.com",
            password="secret_password",
            fluent=fluent,
        )

        sender.send(sample_message)

        mock_smtp_class.assert_called_once_with("smtp.example.com", 587)
        # Check TLS flow
        assert mock_server.ehlo.call_count == 2
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user@example.com", "secret_password")
        mock_server.send_message.assert_called_once_with(sample_message)


def test_smtp_sender_failure(fluent, sample_message):
    with patch("core.smtp_implementations.smtplib.SMTP") as mock_smtp_class:
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        mock_server.login.side_effect = Exception("Auth failed")

        sender = SMTPSenderTLS(
            server="smtp.example.com",
            port=587,
            email="user@example.com",
            password="secret_password",
            fluent=fluent,
        )

        with pytest.raises(EmailSendError) as exc_info:
            sender.send(sample_message)

        assert "log-error-email-send-failed" in str(exc_info.value)
        assert "Auth failed" in str(exc_info.value)
