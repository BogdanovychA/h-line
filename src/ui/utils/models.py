# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from dataclasses import dataclass, field

from flet_storage import FletStorage

from abstract.application_generator import BaseGenerator
from abstract.application_name_creator import BaseNameCreator
from abstract.application_saver import BaseSaver
from abstract.application_sender import BaseSender
from utils.measurement_api import MeasurementAPI


@dataclass
class Officer:
    """Представляє дані про посадову особу"""

    name: str = ""
    position: str = ""
    email: str = ""


@dataclass
class PandorasBox:
    """Контейнер для зберігання основних об'єктів та стану застосунку"""

    storage: FletStorage
    generator: BaseGenerator
    ga: MeasurementAPI
    name_creator: BaseNameCreator
    sender: BaseSender | None = None
    saver: BaseSaver | None = None
    client_id: str = ""
    officer: Officer = field(default_factory=Officer)
