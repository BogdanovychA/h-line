# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from datetime import datetime
from io import BytesIO

import pytest

from models.email_errors import EmailFileNotFoundError
from models.file_type import FileType
from utils.files import (
    create_file_name,
    create_path_dir,
    file_to_buffer,
    get_mime,
    save,
)


class _MockFluent:
    def get(self, key, **kwargs):
        return key


@pytest.fixture
def fluent():
    return _MockFluent()


# --- get_mime ---


def test_get_mime_html():
    maintype, subtype = get_mime("file.html")
    assert maintype == "text"
    assert subtype == "html"


def test_get_mime_docx():
    maintype, subtype = get_mime("file.docx")
    assert maintype == "application"


def test_get_mime_unknown_falls_back_to_octet_stream():
    maintype, subtype = get_mime("file.xyz_unknown_ext_123")
    assert maintype == "application"
    assert subtype == "octet-stream"


# --- create_file_name ---


def test_create_file_name_has_correct_extension():
    assert create_file_name(FileType.DOCX).endswith(".docx")
    assert create_file_name(FileType.MD).endswith(".md")
    assert create_file_name(FileType.HTML).endswith(".html")


def test_create_file_name_starts_with_application():
    assert create_file_name(FileType.DOCX).startswith("application-")


def test_create_file_name_is_unique():
    names = [create_file_name(FileType.MD) for _ in range(20)]
    assert len(set(names)) > 1


# --- file_to_buffer ---


def test_file_to_buffer_reads_content(fluent, tmp_path):
    content = b"test content"
    p = tmp_path / "file.txt"
    p.write_bytes(content)
    buf = file_to_buffer(p, fluent)
    assert buf.read() == content


def test_file_to_buffer_raises_for_missing_file(fluent, tmp_path):
    with pytest.raises(EmailFileNotFoundError):
        file_to_buffer(tmp_path / "nonexistent.docx", fluent)


# --- save ---


def test_save_writes_buffer_to_file(fluent, tmp_path):
    path = tmp_path / "output.txt"
    buf = BytesIO(b"hello")
    result = save(buf, path, fluent)
    assert result == path
    assert path.read_bytes() == b"hello"


def test_save_returns_none_for_none_buffer(fluent, tmp_path):
    result = save(None, tmp_path / "out.txt", fluent)
    assert result is None


def test_save_buffer_position_reset_after_write(fluent, tmp_path):
    path = tmp_path / "output.txt"
    buf = BytesIO(b"data")
    save(buf, path, fluent)
    # After save, buffer should be readable from start again
    assert buf.read() == b"data"


# --- create_path_dir ---


def test_create_path_dir_creates_date_structure(fluent, tmp_path):
    result = create_path_dir(tmp_path, fluent)
    now = datetime.now()
    expected = tmp_path / now.strftime("%Y/%m/%d")
    assert result == expected
    assert result.is_dir()


def test_create_path_dir_idempotent(fluent, tmp_path):
    result1 = create_path_dir(tmp_path, fluent)
    result2 = create_path_dir(tmp_path, fluent)
    assert result1 == result2
