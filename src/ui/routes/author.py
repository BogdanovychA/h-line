# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

import asyncio

import flet as ft

from config import app
from ui.utils import elements, style

TITLE = "Про автора"

ROUTE = app.settings.base_url + "/author"


def button(page) -> ft.Button:
    """Створює кнопку для переходу на сторінку "Про автора" """
    return ft.Button(
        TITLE,
        on_click=lambda: asyncio.create_task(page.push_route(ROUTE)),
    )


def build_view(page: ft.Page) -> ft.View:
    """Будує вікно з інформацією про автора"""
    page.title = TITLE
    return ft.View(
        route=ROUTE,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            elements.app_bar(TITLE),
            ft.Text("Андрій БОГДАНОВИЧ", size=style.settings.text_size),
            ft.Text(""),
            ft.Image(
                src="/images/bogdanovych-900x900.jpg",  # Посилання на картинку
                width=200,
                height=200,
            ),
            ft.Text(""),
            ft.Text(
                size=style.settings.text_size,
                spans=[
                    elements.link("Домашня сторінка", "https://www.bogdanovych.org"),
                ],
            ),
            ft.Text(
                size=style.settings.text_size,
                spans=[
                    elements.link(
                        "Інші застосунки автора", "https://apps.bogdanovych.org"
                    ),
                ],
            ),
            ft.Text(""),
            elements.back_button(page),
        ],
    )
