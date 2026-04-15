# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from enum import StrEnum


class FileType(StrEnum):
    """Типи файлів для шаблонів та згенерованих документів."""

    DOCX = "docx"
    MD = "md"
    HTML = "html"
