# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from abstract.application_generator import BaseTemplateManager, GlobalGenerator
from abstract.application_name_creator import NameCreator
from abstract.application_saver import FileSaver
from abstract.application_sender import EmailSender
from core.email_manager import EmailManager
from models.file_type import FileType
from models.smtp import SMTPProtocol


class _MockFluent:
    def get(self, key, **kwargs):
        return key


@pytest.fixture
def fluent():
    return _MockFluent()


# --- GlobalGenerator Tests ---


class DummyTemplateManager(BaseTemplateManager):
    def __init__(self, template_path: Path, fluent):
        self.template_path = template_path
        self.fluent = fluent

    def generate_application(self, request_data):
        buf = BytesIO(b"Generated Application")
        return buf


def test_global_generator_register_and_get(fluent):
    # Save original registry state
    original_registry = GlobalGenerator._REGISTRY.copy()
    try:
        # Register dummy manager
        GlobalGenerator.register(FileType.HTML, DummyTemplateManager)

        # Retrieve it
        cls = GlobalGenerator.get_generator_class(FileType.HTML, fluent)
        assert cls == DummyTemplateManager
    finally:
        GlobalGenerator._REGISTRY = original_registry


def test_global_generator_get_unregistered_raises(fluent):
    # Save original registry state to avoid side effects
    original_registry = GlobalGenerator._REGISTRY.copy()
    if FileType.MD in GlobalGenerator._REGISTRY:
        del GlobalGenerator._REGISTRY[FileType.MD]
    try:
        # Retrieve unregistered file type
        with pytest.raises(ValueError):
            GlobalGenerator.get_generator_class(FileType.MD, fluent)
    finally:
        GlobalGenerator._REGISTRY = original_registry


def test_global_generator_initialization_and_generation(fluent, monkeypatch):
    original_registry = GlobalGenerator._REGISTRY.copy()
    try:
        GlobalGenerator.register(FileType.HTML, DummyTemplateManager)

        # Mock settings
        monkeypatch.setattr("config.app.settings.template_file_type", FileType.HTML)
        monkeypatch.setattr("config.app.settings.templates_dir", Path("/tmp/templates"))
        monkeypatch.setattr("config.app.settings.template_file_name", "test_doc")

        generator = GlobalGenerator(fluent)
        assert isinstance(generator.creator, DummyTemplateManager)
        assert generator.creator.template_path == Path("/tmp/templates/test_doc.html")

        mock_request = MagicMock()
        result = generator.generate_application(mock_request)
        assert result.read() == b"Generated Application"
    finally:
        GlobalGenerator._REGISTRY = original_registry


# --- NameCreator Tests ---


def test_name_creator():
    name_creator = NameCreator()
    with patch(
        "abstract.application_name_creator.files.create_file_name"
    ) as mock_create_name:
        mock_create_name.return_value = "generated-name.docx"

        result = name_creator.create_file_name(FileType.DOCX)
        assert result == "generated-name.docx"
        mock_create_name.assert_called_once_with(FileType.DOCX)


# --- FileSaver Tests ---


def test_file_saver(fluent, monkeypatch):
    monkeypatch.setattr("config.app.settings.output_dir", Path("/tmp/output"))

    saver = FileSaver(fluent)
    assert saver.output_dir == Path("/tmp/output")

    buf = BytesIO(b"file content")
    file_name = "test_file.docx"

    with (
        patch("abstract.application_saver.files.create_path_dir") as mock_create_dir,
        patch("abstract.application_saver.files.save") as mock_save,
    ):
        mock_create_dir.return_value = Path("/tmp/output/2026/06/26")

        saver.save(buf, file_name)

        mock_create_dir.assert_called_once_with(Path("/tmp/output"), fluent=fluent)
        mock_save.assert_called_once_with(
            buf, Path("/tmp/output/2026/06/26/test_file.docx"), fluent=fluent
        )
        # Check buffer seek position reset
        assert buf.tell() == 0


# --- EmailSender Tests ---


class DummySMTPSender:
    def __init__(self, server, port, email, password, fluent):
        self.server = server
        self.port = port
        self.email = email
        self.password = password
        self.fluent = fluent
        self.sent_messages = []

    def send(self, message):
        self.sent_messages.append(message)


def test_email_sender(fluent, monkeypatch):
    # Register our DummySMTPSender under SMTPProtocol.TLS
    original_registry = EmailManager._REGISTRY.copy()
    EmailManager._REGISTRY[SMTPProtocol.TLS] = DummySMTPSender

    try:
        # Mock sender and recipient settings
        monkeypatch.setattr("config.email_sender.settings.email", "sender@example.com")
        monkeypatch.setattr("config.email_sender.settings.protocol", SMTPProtocol.TLS)
        monkeypatch.setattr("config.email_sender.settings.server", "smtp.example.com")
        monkeypatch.setattr("config.email_sender.settings.port", 587)
        monkeypatch.setattr("config.email_sender.settings.password", "pass")

        monkeypatch.setattr(
            "config.email_recipient.settings.to", "recipient@example.com"
        )
        monkeypatch.setattr("config.email_recipient.settings.cc", "cc1@example.com")
        monkeypatch.setattr("config.email_recipient.settings.bcc", "bcc1@example.com")

        # Create sender
        sender = EmailSender(
            fluent,
            cc_recipients=["cc2@example.com"],
            bcc_recipients=["bcc2@example.com"],
        )

        # Verify the underlying DummySMTPSender protocol configuration
        assert isinstance(sender.manager.protocol, DummySMTPSender)
        assert sender.manager.protocol.server == "smtp.example.com"
        assert sender.manager.protocol.port == 587
        assert sender.manager.protocol.email == "sender@example.com"
        assert sender.manager.protocol.password == "pass"

        # Mock the message factory create_message
        mock_message = MagicMock()
        with patch.object(
            sender.message_factory, "create_message", return_value=mock_message
        ) as mock_create_msg:
            buf = BytesIO(b"pdf data")
            sender.send(buf, "appeal.pdf")

            mock_create_msg.assert_called_once_with(buf, "appeal.pdf")
            assert mock_message in sender.manager.protocol.sent_messages

    finally:
        # Restore registry
        EmailManager._REGISTRY = original_registry
