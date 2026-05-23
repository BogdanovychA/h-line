# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from enum import StrEnum


class LoggingLevel(StrEnum):
    """Доступні рівні логування для програми."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EventName(StrEnum):
    ROUTE_CHANGE = "route_change"
    APPLICATION_CREATE = "application_create"


class Analytics(StrEnum):
    NO_PLATFORM = "no_platform"
