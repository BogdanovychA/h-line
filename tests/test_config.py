# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from config.app import Settings as AppSettings
from config.email_recipient import Settings as RecipientSettings
from config.email_sender import Settings as SenderSettings
from config.google_analytics import Settings as AnalyticsSettings
from config.server import Settings as ServerSettings
from models.file_type import FileType
from models.logging import LoggingLevel
from models.smtp import SMTPProtocol


def test_app_settings_env_override(monkeypatch):
    monkeypatch.setenv("APP__TEMPLATE_FILE_TYPE", "html")
    monkeypatch.setenv("APP__SEND_TO_EMAIL", "False")
    monkeypatch.setenv("APP__TEMPLATE_FILE_NAME", "my_app_template")

    settings = AppSettings()
    assert settings.template_file_type == FileType.HTML
    assert settings.send_to_email is False
    assert settings.template_file_name == "my_app_template"


def test_email_sender_settings_env_override(monkeypatch):
    monkeypatch.setenv("EMAIL_SENDER__SERVER", "smtp.custom.com")
    monkeypatch.setenv("EMAIL_SENDER__PORT", "587")
    monkeypatch.setenv("EMAIL_SENDER__EMAIL", "test@custom.com")
    monkeypatch.setenv("EMAIL_SENDER__PASSWORD", "mypassword")
    monkeypatch.setenv("EMAIL_SENDER__PROTOCOL", "TLS")

    settings = SenderSettings()
    assert settings.server == "smtp.custom.com"
    assert settings.port == 587
    assert settings.email == "test@custom.com"
    assert settings.password == "mypassword"
    assert settings.protocol == SMTPProtocol.TLS


def test_email_recipient_settings_env_override(monkeypatch):
    monkeypatch.setenv("EMAIL_RECIPIENT__TO", "to@example.com")
    monkeypatch.setenv("EMAIL_RECIPIENT__CC", "cc@example.com")
    monkeypatch.setenv("EMAIL_RECIPIENT__BCC", "bcc@example.com")

    settings = RecipientSettings()
    assert settings.to == "to@example.com"
    assert settings.cc == "cc@example.com"
    assert settings.bcc == "bcc@example.com"


def test_google_analytics_settings_env_override(monkeypatch):
    monkeypatch.setenv("GOOGLE_ANALYTICS__SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("GOOGLE_ANALYTICS__ID", "UA-XXXXX-Y")

    settings = AnalyticsSettings()
    assert settings.secret_key == "test_secret_key"
    assert settings.id == "UA-XXXXX-Y"


def test_server_settings_env_override(monkeypatch):
    monkeypatch.setenv("SERVER__LOGGING_LEVEL", "ERROR")

    settings = ServerSettings()
    assert settings.logging_level == LoggingLevel.ERROR
