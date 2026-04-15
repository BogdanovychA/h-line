# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from enum import StrEnum


class SMTPProtokol(StrEnum):
    """Типи протоколів шифрування SMTP-з'єднання."""

    SSL = "SSL"
    TLS = "TLS"
