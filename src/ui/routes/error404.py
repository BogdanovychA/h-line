# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.utils.models import PandorasBox

import flet as ft

from config import app
from ui.utils import elements, style

ROUTE = app.settings.base_url + "/404"


def build_view(page: ft.Page, box: PandorasBox) -> ft.View:
    """Будує вікно для відображення помилки 404 (Сторінка не знайдена)"""

    return ft.View(
        route=ROUTE,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            elements.app_bar(box.fluent.get("error-404-title"), page),
            ft.Text(""),
            ft.Text(box.fluent.get("error-404-title"), size=style.settings.text_size),
            ft.Text(box.fluent.get("target-page", route=page.route)),
            ft.Text(""),
            elements.back_button(page, box.fluent.get("back")),
        ],
    )
