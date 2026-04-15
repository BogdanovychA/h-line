# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.file_type import FileType

from abc import ABC, abstractmethod

from utils import files


class BaseNameCreator(ABC):
    """Базовий клас для створення імен файлів звернень."""

    @abstractmethod
    def create_file_name(self, file_type: FileType) -> str:
        """Створює назву файлу на основі типу файлу."""
        pass


class NameCreator(BaseNameCreator):
    """Стандартний створювач імен файлів."""

    def create_file_name(self, file_type: FileType) -> str:
        """Створює назву файлу, використовуючи утиліту створення імен."""
        return files.create_file_name(file_type)
