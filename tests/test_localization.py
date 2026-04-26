# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

import os
from pathlib import Path

import pytest
from fluent_manager import FluentManager

# Шлях до локалей (відносний до кореня проєкту)
LOCALES_PATH = Path("src/assets/locales")


@pytest.fixture
def fluent():
    """Фікстура для створення об'єкта FluentManager."""
    return FluentManager(
        locales=["uk"],
        locales_path=str(LOCALES_PATH),
        default_locale="uk",
    )


def test_ui_localization(fluent):
    """Перевірка локалізації інтерфейсу."""
    assert fluent.get("app-title") == '"Гаряча лінія" Держенергонагляду (H-Line)'
    assert fluent.get("application-title") == "Фіксація звернення"
    assert fluent.get("back") == "Назад"


def test_mail_localization(fluent):
    """Перевірка локалізації пошти (з параметрами)."""
    filename = "test_file.docx"
    subject = fluent.get("email-subject", filename=filename)
    assert filename in subject
    assert "Звернення" in subject

    body = fluent.get("email-body", filename=filename)
    assert filename in body
    assert "Держенергонагляд" in body


def test_logs_localization(fluent):
    """Перевірка локалізації логів."""
    assert fluent.get("log-error-generate-file") == "Помилка при генерації файлу"

    protocol = "SMTPSenderTLS"
    smtp_err = fluent.get("log-error-smtp-critical", protocol=protocol)
    assert protocol in smtp_err
    assert "Критична помилка SMTP" in smtp_err


def test_fallback_mechanism(fluent):
    """Перевірка механізму фолбеку для неіснуючих ключів."""
    non_existent_key = "non-existent-key-12345"
    assert fluent.get(non_existent_key) == non_existent_key


def test_locales_directory_exists():
    """Перевірка наявності директорії з локалями."""
    assert LOCALES_PATH.exists()
    assert (LOCALES_PATH / "uk").exists()
    assert (LOCALES_PATH / "uk" / "ui.ftl").exists()
    assert (LOCALES_PATH / "uk" / "mail.ftl").exists()
    assert (LOCALES_PATH / "uk" / "logs.ftl").exists()
