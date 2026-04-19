# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.utils.models import PandorasBox

import asyncio

import flet as ft

from config import app
from ui.utils import elements, style

ROUTE = app.settings.base_url + "/about"


def button(page, text: str = "Про застосунок") -> ft.Button:
    """Створює кнопку для переходу на сторінку "Про застосунок" """
    return ft.Button(
        text,
        on_click=lambda: asyncio.create_task(page.push_route(ROUTE)),
    )


def build_view(page: ft.Page, box: PandorasBox) -> ft.View:
    """Будує вікно з інформацією про застосунок"""
    page.title = box.fluent.get("about-title")
    return ft.View(
        route=ROUTE,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            elements.app_bar(box.fluent.get("about-title")),
            ft.Text("H-Line", size=style.settings.text_size),
            ft.Text(box.fluent.get("version", version=app.settings.version)),
            ft.Text(box.fluent.get("license", license=app.settings.license)),
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
                    elements.link(
                        box.fluent.get("github"),
                        "https://github.com/BogdanovychA/h-line",
                    ),
                ],
            ),
            ft.Text(
                size=style.settings.text_size,
                spans=[
                    elements.link(
                        box.fluent.get("sies"),
                        "https://sies.gov.ua/",
                    ),
                ],
            ),
            ft.Text(""),
            elements.back_button(page, box.fluent.get("back")),
        ],
    )
