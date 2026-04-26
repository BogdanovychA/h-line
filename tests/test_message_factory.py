# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from io import BytesIO
from pathlib import Path

import pytest
from fluent_manager import FluentManager

from core.message_factory import AppealMessageFactory

LOCALES_PATH = Path("src/assets/locales")


@pytest.fixture
def fluent():
    return FluentManager(
        locales=["uk"],
        locales_path=str(LOCALES_PATH),
        default_locale="uk",
    )


@pytest.fixture
def factory(fluent):
    return AppealMessageFactory(
        fluent=fluent,
        sender_email="sender@example.com",
        recipient_list=["to@example.com"],
    )


def _make_buf():
    return BytesIO(b"file content")


def test_from_header(factory):
    msg = factory.create_message(_make_buf(), "appeal.docx")
    assert msg["From"] == "sender@example.com"


def test_to_header(factory):
    msg = factory.create_message(_make_buf(), "appeal.docx")
    assert "to@example.com" in msg["To"]


def test_subject_contains_filename(factory):
    msg = factory.create_message(_make_buf(), "appeal.docx")
    assert "appeal.docx" in msg["Subject"]


def test_cc_set_when_provided(fluent):
    factory = AppealMessageFactory(
        fluent=fluent,
        sender_email="sender@example.com",
        recipient_list=["to@example.com"],
        cc_recipients=["cc@example.com"],
    )
    msg = factory.create_message(_make_buf(), "file.docx")
    assert "cc@example.com" in msg["Cc"]


def test_cc_absent_when_not_provided(factory):
    msg = factory.create_message(_make_buf(), "file.docx")
    assert msg["Cc"] is None


def test_bcc_set_when_provided(fluent):
    factory = AppealMessageFactory(
        fluent=fluent,
        sender_email="sender@example.com",
        recipient_list=["to@example.com"],
        bcc_recipients=["bcc@example.com"],
    )
    msg = factory.create_message(_make_buf(), "file.docx")
    assert "bcc@example.com" in msg["Bcc"]


def test_bcc_absent_when_not_provided(factory):
    msg = factory.create_message(_make_buf(), "file.docx")
    assert msg["Bcc"] is None


def test_attachment_present(factory):
    msg = factory.create_message(_make_buf(), "appeal.docx")
    payloads = msg.get_payload()
    filenames = [p.get_filename() for p in payloads if hasattr(p, "get_filename")]
    assert "appeal.docx" in filenames


def test_multiple_recipients_joined_in_to(fluent):
    factory = AppealMessageFactory(
        fluent=fluent,
        sender_email="sender@example.com",
        recipient_list=["a@example.com", "b@example.com"],
    )
    assert "a@example.com" in factory.to_str
    assert "b@example.com" in factory.to_str
