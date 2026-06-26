# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from email.message import EmailMessage
    from io import BytesIO

from utils import files


def add_attachment_from_buffer(
    msg: EmailMessage, buffer: BytesIO, file_name: str
) -> None:
    """Додає вкладення до електронного листа з буфера BytesIO."""

    maintype, subtype = files.get_mime(file_name)

    buffer.seek(0)

    msg.add_attachment(
        buffer.read(),
        maintype=maintype,
        subtype=subtype,
        filename=file_name,
    )

    buffer.seek(0)
