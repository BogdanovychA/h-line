# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fluent_manager import FluentManager

from core.email_manager import EmailManager
from core.smtp_implementations import SMTPSenderBase
from models.smtp import SMTPProtocol

LOCALES_PATH = Path("src/assets/locales")


@pytest.fixture
def fluent():
    return FluentManager(
        locales=["uk"],
        locales_path=str(LOCALES_PATH),
        default_locale="uk",
    )


@pytest.fixture(autouse=True)
def isolate_registry():
    saved = EmailManager._REGISTRY.copy()
    EmailManager._REGISTRY.clear()
    yield
    EmailManager._REGISTRY.clear()
    EmailManager._REGISTRY.update(saved)


def test_register_and_retrieve_protocol(fluent):
    mock_class = MagicMock(spec=SMTPSenderBase)
    EmailManager.register(SMTPProtocol.TLS, mock_class)
    result = EmailManager.get_protocol_class(SMTPProtocol.TLS, fluent)
    assert result is mock_class


def test_get_unregistered_protocol_raises_value_error(fluent):
    with pytest.raises(ValueError):
        EmailManager.get_protocol_class(SMTPProtocol.SSL, fluent)


def test_register_overwrites_existing(fluent):
    first = MagicMock(spec=SMTPSenderBase)
    second = MagicMock(spec=SMTPSenderBase)
    EmailManager.register(SMTPProtocol.SSL, first)
    EmailManager.register(SMTPProtocol.SSL, second)
    assert EmailManager.get_protocol_class(SMTPProtocol.SSL, fluent) is second


def test_send_delegates_to_protocol():
    mock_sender = MagicMock()
    manager = EmailManager(sender_protocol=mock_sender)
    mock_msg = MagicMock()
    manager.send(mock_msg)
    mock_sender.send.assert_called_once_with(mock_msg)
