# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from models.email_errors import EmailError, EmailSendError
from models.file_type import FileType
from models.logging import Analytics, EventName, LoggingLevel
from models.smtp import SMTPProtocol


def test_smtp_protocol_values():
    assert SMTPProtocol.SSL == "SSL"
    assert SMTPProtocol.TLS == "TLS"
    assert list(SMTPProtocol) == ["SSL", "TLS"]


def test_file_type_values():
    assert FileType.DOCX == "docx"
    assert FileType.MD == "md"
    assert FileType.HTML == "html"
    assert list(FileType) == ["docx", "md", "html"]


def test_logging_level_values():
    assert LoggingLevel.DEBUG == "DEBUG"
    assert LoggingLevel.INFO == "INFO"
    assert LoggingLevel.WARNING == "WARNING"
    assert LoggingLevel.ERROR == "ERROR"
    assert LoggingLevel.CRITICAL == "CRITICAL"


def test_event_name_values():
    assert EventName.ROUTE_CHANGE == "route_change"
    assert EventName.APPLICATION_CREATE == "application_create"


def test_analytics_values():
    assert Analytics.NO_PLATFORM == "no_platform"


def test_email_errors():
    err = EmailSendError("some message")
    assert isinstance(err, EmailError)
    assert isinstance(err, Exception)
    assert str(err) == "some message"
