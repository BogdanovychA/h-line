# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from __future__ import annotations

import logging
from io import BytesIO
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader, StrictUndefined

if TYPE_CHECKING:
    from pathlib import Path
    from fluent_manager import FluentManager

    from models.appeal_request import AppealRequest

from abstract.application_generator import BaseTemplateManager

logger = logging.getLogger(__name__)


class TxtManager(BaseTemplateManager):
    """Менеджер для генерації текстових файлів на основі шаблонів Jinja2."""

    def __init__(self, template_path: Path, fluent: FluentManager):
        """Ініціалізує менеджер шляхом до шаблону Jinja2."""
        self.template_dir = template_path.parent
        self.template_name = template_path.name
        self.fluent = fluent

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            undefined=StrictUndefined,
        )

    def generate_application(self, request_data: AppealRequest) -> BytesIO | None:
        """Генерує файл звернення у текстовому форматі."""
        try:
            template = self.env.get_template(self.template_name)
            rendered_text = template.render(request_data.get_context())

            buffer = BytesIO()
            buffer.write(rendered_text.encode("utf-8"))

            buffer.seek(0)
            return buffer

        except Exception:
            logger.exception(self.fluent.get("log-error-generate-file"))
            return None
