# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from io import BytesIO

from abc import ABC, abstractmethod

from config import email_recipient, email_sender
from core.email_manager import EmailManager
from core.message_factory import AppealMessageFactory


class BaseSender(ABC):
    """Базовий клас для відправки згенерованих звернень."""

    @abstractmethod
    def send(self, buffer: BytesIO, file_name: str) -> None:
        """Відправляє файл звернення."""
        pass


class EmailSender(BaseSender):
    """Клас для відправки звернень електронною поштою."""

    def __init__(
        self, cc_recipients: list | None = None, bcc_recipients: list | None = None
    ):
        """Ініціалізація відправника електронної пошти з налаштуваннями SMTP та одержувачів."""

        cc = cc_recipients or []
        bcc = bcc_recipients or []

        self.message_factory = AppealMessageFactory(
            sender_email=email_sender.settings.email,
            recipient_list=[email_recipient.settings.to],
            cc_recipients=[email_recipient.settings.cc, *cc],
            bcc_recipients=[email_recipient.settings.bcc, *bcc],
        )

        protokol_class = EmailManager.get_protokol_class(email_sender.settings.protokol)

        protokol = protokol_class(
            email_sender.settings.server,
            email_sender.settings.port,
            email_sender.settings.email,
            email_sender.settings.password,
        )

        self.manager = EmailManager(protokol)

    def send(self, buffer: BytesIO, file_name: str) -> None:
        """Створює повідомлення та відправляє його через SMTP."""
        message = self.message_factory.create_message(buffer, file_name)
        self.manager.send(message)
