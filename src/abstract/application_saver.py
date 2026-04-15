# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from io import BytesIO

from abc import ABC, abstractmethod

from config import app
from utils import files


class BaseSaver(ABC):
    """Базовий клас для збереження згенерованих звернень."""

    @abstractmethod
    def save(self, buffer: BytesIO, file_name: str) -> None:
        """Зберігає вміст буфера у файл."""
        pass


class FileSaver(BaseSaver):
    """Клас для збереження звернень у файлову систему."""

    def __init__(self) -> None:
        """Ініціалізація збережувача з директорією виводу."""
        self.output_dir = app.settings.output_dir

    def save(self, buffer: BytesIO, file_name: str) -> None:
        """Зберігає буфер у файл у вказаній директорії."""
        dir_name = files.create_path_dir(self.output_dir)
        path = dir_name / file_name

        buffer.seek(0)
        files.save(buffer, path)
        buffer.seek(0)
