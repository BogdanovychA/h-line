# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from __future__ import annotations

import logging
from email.message import EmailMessage
from typing import TYPE_CHECKING, ClassVar, Type

if TYPE_CHECKING:
    from fluent_manager import FluentManager

from core.smtp_implementations import SMTPSenderBase
from models.smtp import SMTPProtocol

logger = logging.getLogger(__name__)


class EmailManager:
    """Універсальний менеджер для відправки готових об'єктів EmailMessage."""

    _REGISTRY: ClassVar[dict[SMTPProtocol, Type[SMTPSenderBase]]] = {}

    @classmethod
    def register(
        cls, protocol_type: SMTPProtocol, protocol_class: Type[SMTPSenderBase]
    ) -> None:
        """Реєстрація конкретного класу реалізації SMTP-шифрування"""
        cls._REGISTRY[protocol_type] = protocol_class

    @classmethod
    def get_protocol_class(
        cls, protocol_type: SMTPProtocol, fluent: FluentManager
    ) -> Type[SMTPSenderBase]:
        """Повертає зареєстрований клас протоколу або викидає помилку."""
        if protocol_type not in cls._REGISTRY:
            msg = fluent.get(
                "log-error-protocol-not-registered", protocol=str(protocol_type)
            )
            raise ValueError(msg)
        return cls._REGISTRY[protocol_type]

    def __init__(self, sender_protocol: SMTPSenderBase) -> None:
        """Ініціалізація менеджера електронної пошти конкретним протоколом відправки."""
        self.protocol = sender_protocol

    def send(self, message: EmailMessage) -> None:
        """Відправляє готовий об'єкт EmailMessage."""
        self.protocol.send(message)
