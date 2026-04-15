# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

import asyncio

import flet as ft

from config import app
from ui.utils import elements, style

TITLE = "Про застосунок"

ROUTE = app.settings.base_url + "/about"


def button(page) -> ft.Button:
    """Створює кнопку для переходу на сторінку "Про застосунок" """
    return ft.Button(
        TITLE,
        on_click=lambda: asyncio.create_task(page.push_route(ROUTE)),
    )


def build_view(page: ft.Page) -> ft.View:
    """Будує вікно з інформацією про застосунок"""
    page.title = TITLE
    return ft.View(
        route=ROUTE,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            elements.app_bar(TITLE),
            ft.Text("H-Line", size=style.settings.text_size),
            ft.Text(f"Версія: {app.settings.version}"),
            ft.Text(f"Ліцензія: {app.settings.license}"),
            ft.Text(""),
            ft.Image(
                src="/images/h-line-logo-no_bg.png",
                width=200,
                height=200,
            ),
            ft.Text(""),
            ft.Text(
                size=style.settings.text_size,
                spans=[
                    elements.link("GitHub", "https://github.com/BogdanovychA/h-line"),
                ],
            ),
            ft.Text(
                size=style.settings.text_size,
                spans=[
                    elements.link("Держенергонагляд", "https://sies.gov.ua/"),
                ],
            ),
            ft.Text(""),
            elements.back_button(page),
        ],
    )
