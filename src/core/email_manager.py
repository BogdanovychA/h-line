# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

import logging
from email.message import EmailMessage
from typing import ClassVar, Type

from core.smtp_implementations import SMTPSenderBase
from models.smtp import SMTPProtokol

logger = logging.getLogger(__name__)


class EmailManager:
    """Універсальний менеджер для відправки готових об'єктів EmailMessage."""

    _REGISTRY: ClassVar[dict[SMTPProtokol, Type[SMTPSenderBase]]] = {}

    @classmethod
    def register(
        cls, protokol_type: SMTPProtokol, protokol_class: Type[SMTPSenderBase]
    ) -> None:
        """Реєстрація конкретного класу реалізації SMTP-шифрування"""
        cls._REGISTRY[protokol_type] = protokol_class

    @classmethod
    def get_protokol_class(cls, protokol_type: SMTPProtokol) -> Type[SMTPSenderBase]:
        """Повертає зареєстрований клас протоколу або викидає помилку."""
        if protokol_type not in cls._REGISTRY:
            raise ValueError(f"Реалізація {protokol_type} не зареєстрована!")
        return cls._REGISTRY[protokol_type]

    def __init__(self, sender_protokol: SMTPSenderBase) -> None:
        """Ініціалізація менеджера електронної пошти конкретним протоколом відправки."""
        self.protokol = sender_protokol

    def send(self, message: EmailMessage) -> None:
        """Відправляє готовий об'єкт EmailMessage."""
        self.protokol.send(message)
