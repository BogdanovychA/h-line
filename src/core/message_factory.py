# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from email.message import EmailMessage
from io import BytesIO

from utils import emails


class AppealMessageFactory:
    """Фабрика для створення об'єктів EmailMessage для звернень."""

    def __init__(
        self,
        sender_email: str,
        recipient_list: list[str],
        cc_recipients: list[str] | None = None,
        bcc_recipients: list[str] | None = None,
    ) -> None:
        """Ініціалізація фабрики повідомлень параметрами відправника та одержувачів."""
        self.sender_email = sender_email
        self.to_str = ", ".join(recipient_list)
        self.cc_str = ", ".join(cc_recipients) if cc_recipients else None
        self.bcc_str = ", ".join(bcc_recipients) if bcc_recipients else None

    def create_message(self, buffer: BytesIO, file_name: str) -> EmailMessage:
        """Створює об'єкт EmailMessage з вкладенням із буфера."""
        msg = EmailMessage()

        msg['Subject'] = f"Звернення на гарячу лінію: {file_name}"
        msg['From'] = self.sender_email
        msg['To'] = self.to_str

        if self.cc_str:
            msg['Cc'] = self.cc_str

        if self.bcc_str:
            msg['Bcc'] = self.bcc_str

        msg.set_content(
            f'Звернення на "гарячу лінію" Держенергонагляду у додатку до цього листа.\n\n'
            f"Назва файлу: {file_name}"
        )

        emails.add_attachment_from_buffer(msg, buffer, file_name)

        return msg
