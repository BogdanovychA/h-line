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
    from models.appeal_request import AppealRequest
    from pathlib import Path

from docxtpl import DocxTemplate

logger = logging.getLogger(__name__)


from abstract.application_generator import BaseTemplateManager


class DocManager(BaseTemplateManager):
    """Менеджер для генерації DOCX-файлів на основі шаблонів."""

    def __init__(self, template_path: Path):
        """Ініціалізує менеджер шляхом до шаблону."""
        self.template = template_path

    def generate_application(self, request_data: AppealRequest) -> BytesIO | None:
        """Генерує файл звернення у форматі DOCX."""

        try:
            doc = DocxTemplate(self.template)
            doc.render(request_data.get_context())

            buffer = BytesIO()
            doc.save(buffer)

            buffer.seek(0)

            return buffer

        except Exception:
            logger.exception("Помилка при генерації файлу")
            return None
