# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.appeal_request import AppealRequest
    from io import BytesIO

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar, Type

if TYPE_CHECKING:
    from models.appeal_request import AppealRequest
    from io import BytesIO
    from pathlib import Path

from config import app
from models.file_type import FileType


class BaseTemplateManager(ABC):
    """Інтерфейс для менеджерів, що працюють з конкретними форматами шаблонів (Docx, Jinja2 тощо)"""

    @abstractmethod
    def __init__(self, template_path: Path):
        """Ініціалізація менеджера шаблонів."""
        pass

    @abstractmethod
    def generate_application(self, request_data: AppealRequest) -> BytesIO | None:
        """Генерує файл звернення на основі даних запиту."""
        pass


class BaseGenerator(ABC):
    """Загальний інтерфейс генератора для UI"""

    @property
    @abstractmethod
    def file_type(self) -> FileType:
        """Повертає тип файлу, який генерує цей генератор."""
        pass

    @abstractmethod
    def generate_application(self, request_data: AppealRequest) -> BytesIO | None:
        """Генерує файл звернення."""
        pass


class GlobalGenerator(BaseGenerator):
    """Глобальний генератор, який використовує зареєстровані менеджери шаблонів."""

    _REGISTRY: ClassVar[dict[FileType, Type[BaseTemplateManager]]] = {}

    @classmethod
    def register(
        cls, file_type: FileType, generator_class: Type[BaseTemplateManager]
    ) -> None:
        """Реєстрація конкретного класу генератора для певного типу файлу."""
        cls._REGISTRY[file_type] = generator_class

    @classmethod
    def get_generator_class(cls, file_type: FileType) -> Type[BaseTemplateManager]:
        """Повертає зареєстрований клас генератора або викидає помилку."""
        if file_type not in cls._REGISTRY:
            raise ValueError(f"Генератор для типу {file_type} не зареєстрований!")
        return cls._REGISTRY[file_type]

    @property
    def file_type(self):
        """Повертає тип файлу з налаштувань додатка."""
        return app.settings.template_file_type

    def __init__(self) -> None:
        """Ініціалізація глобального генератора на основі налаштувань."""

        generator_class = self.get_generator_class(self.file_type)

        self.creator: BaseTemplateManager = generator_class(
            app.settings.templates_dir
            / f"{app.settings.template_file_name}.{self.file_type}",
        )

    def generate_application(self, request_data: AppealRequest) -> BytesIO | None:
        """Генерує звернення за допомогою вибраного менеджера шаблонів."""
        return self.creator.generate_application(request_data)
