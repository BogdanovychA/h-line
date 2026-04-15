# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

import flet as ft

from config import app
from ui.utils import elements, style

TITLE = "Сторінка не знайдена"
ROUTE = app.settings.base_url + "/404"


def build_view(page: ft.Page) -> ft.View:
    """Будує вікно для відображення помилки 404 (Сторінка не знайдена)"""

    return ft.View(
        route=ROUTE,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            elements.app_bar(TITLE),
            ft.Text(""),
            ft.Text(TITLE, size=style.settings.text_size),
            ft.Text(f"Цільова сторінка: {page.route}"),
            ft.Text(""),
            elements.back_button(page),
        ],
    )
