# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from __future__ import annotations

import logging
from io import BytesIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from models.file_type import FileType
    from fluent_manager import FluentManager

import uuid
from datetime import datetime
from mimetypes import guess_type

from models.email_errors import EmailFileNotFoundError

logger = logging.getLogger(__name__)


def get_mime(file: Path | str) -> tuple[str, str]:
    """Повертає MIME-тип файлу (maintype, subtype)."""
    mime_type, _ = guess_type(str(file))
    if mime_type is None:
        mime_type = "application/octet-stream"

    maintype, subtype = mime_type.split("/", 1)
    return maintype, subtype


def create_file_name(file_type: FileType) -> str:
    """Створює унікальну назву файлу на основі поточного часу та UUID."""

    now = datetime.now()

    file_name = (
        now.strftime("application-%H%M%S") + f"-{uuid.uuid4().hex[:4]}.{file_type}"
    )

    return file_name


def create_path_dir(output_dir: Path, fluent: FluentManager | None = None) -> Path:
    """Створює структуру каталогів на основі поточної дати (рік/місяць/день)."""

    now = datetime.now()

    dir_name = output_dir / now.strftime("%Y/%m/%d")

    try:
        dir_name.mkdir(parents=True, exist_ok=True)
        return dir_name
    except PermissionError:
        msg = (
            fluent.get("log-error-access-create-dir")
            if fluent
            else "Помилка прав доступу при створенні каталогу"
        )
        logger.exception(msg)
        raise PermissionError


def create_path(
    output_dir: Path, file_type: FileType, fluent: FluentManager | None = None
) -> Path:
    """Створює повний шлях до нового файлу звернення."""

    dir_name = create_path_dir(output_dir, fluent=fluent)
    file_name = create_file_name(file_type)

    return dir_name / file_name


def file_to_buffer(file_path: Path) -> BytesIO:
    """Зчитує файл у буфер BytesIO."""

    if not file_path.is_file():
        raise EmailFileNotFoundError(f"Файл не знайдено: {file_path}")

    buffer = BytesIO(file_path.read_bytes())
    buffer.seek(0)

    return buffer


def save(
    buffer: BytesIO | None, path: Path, fluent: FluentManager | None = None
) -> Path | None:
    """Зберігає вміст буфера у файл за вказаним шляхом."""
    if buffer is None:
        msg = fluent.get("log-error-buffer-is-none") if fluent else "BytesIO is None"
        logger.error(msg)
        return None

    buffer.seek(0)

    try:
        path.write_bytes(buffer.read())
        return path

    except PermissionError:
        msg = (
            fluent.get("log-error-access-save-file")
            if fluent
            else "Помилка прав доступу при збереженні файлу"
        )
        logger.exception(msg)
        raise PermissionError

    except Exception:
        msg = (
            fluent.get("log-error-save-file") if fluent else "Помилка збереження файлу"
        )
        logger.exception(msg)
        return None
    finally:
        buffer.seek(0)
