# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.email_manager import EmailMessage

import smtplib
from abc import ABC, abstractmethod

from models.email_errors import EmailSendError

logger = logging.getLogger(__name__)


class SMTPSenderBase(ABC):
    """Базовий клас для відправлення листів через SMTP."""

    def __init__(
        self,
        server: str,
        port: int,
        email: str,
        password: str,
    ) -> None:
        """Ініціалізує параметри підключення до сервера."""
        self.server = server
        self.port = port
        self.email = email
        self.password = password

    @abstractmethod
    def _get_connection(self):
        """Повертає об'єкт SMTP клієнта."""
        pass

    def _setup_connection(self, server: smtplib.SMTP) -> None:
        """Додаткове налаштування з'єднання (наприклад, STARTTLS)."""
        pass

    def send(self, message: EmailMessage) -> None:
        """Відправляє повідомлення."""
        try:
            with self._get_connection() as server:
                self._setup_connection(server)
                server.login(self.email, self.password)
                server.send_message(message)

                logger.info(f"Лист успішно відправлено на {message['To']}")

        except Exception as e:
            logger.exception(f"Критична помилка SMTP ({self.__class__.__name__})")
            raise EmailSendError(f"Не вдалося відправити лист: {e}")


class SMTPSenderSSL(SMTPSenderBase):
    """
    Відправник SMTP з використанням SSL.
    """

    def _get_connection(self):
        """Повертає SMTP_SSL з'єднання."""
        return smtplib.SMTP_SSL(self.server, self.port)


class SMTPSenderTLS(SMTPSenderBase):
    """
    Відправник SMTP з використанням STARTTLS.
    """

    def _get_connection(self):
        """Повертає стандартне SMTP з'єднання."""
        return smtplib.SMTP(self.server, self.port)

    def _setup_connection(self, server: smtplib.SMTP) -> None:
        """Налаштовує STARTTLS для з'єднання."""
        server.ehlo()
        server.starttls()
        server.ehlo()
