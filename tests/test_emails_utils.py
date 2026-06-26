# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from email.message import EmailMessage
from io import BytesIO

from utils.emails import add_attachment_from_buffer


def test_add_attachment_from_buffer():
    msg = EmailMessage()
    buf = BytesIO(b"dummy pdf content")
    file_name = "report.pdf"

    add_attachment_from_buffer(msg, buf, file_name)

    payloads = msg.get_payload()
    assert isinstance(payloads, list)
    assert len(payloads) == 1
    part = payloads[0]
    assert part.get_filename() == "report.pdf"
    assert part.get_content_type() == "application/pdf"
    assert part.get_payload(decode=True) == b"dummy pdf content"
    assert buf.tell() == 0
