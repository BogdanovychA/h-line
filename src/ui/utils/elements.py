# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

import asyncio

import flet as ft

from ui.routes import root
from ui.utils import style


def back_button(page) -> ft.Button:
    """Створює кнопку для повернення на головну сторінку"""
    return ft.Button(
        "Назад",
        icon=ft.Icons.ARROW_BACK,
        on_click=lambda: asyncio.create_task(page.push_route(root.ROUTE)),
    )


def app_bar(title) -> ft.AppBar:
    """Створює панель застосунку (AppBar) з вказаним заголовком"""
    return ft.AppBar(
        title=ft.Text(title, size=style.settings.title_size, weight=ft.FontWeight.BOLD),
        center_title=True,
        bgcolor=ft.Colors.SURFACE_CONTAINER,
    )


def link(text: str, url: str) -> ft.TextSpan:
    """Створює текстове посилання з ефектом наведення"""
    style_normal = ft.TextStyle(
        decoration=ft.TextDecoration.NONE, color=style.settings.link_color
    )
    style_hover = ft.TextStyle(
        decoration=ft.TextDecoration.UNDERLINE, color=style.settings.link_color
    )

    def _handler(event: ft.Event) -> None:
        """Обробник подій наведення та виходу курсору для посилання"""
        span.style = style_hover if event.name == "enter" else style_normal
        span.update()

    span = ft.TextSpan(
        text,
        url=url,
        style=style_normal,
        on_enter=_handler,
        on_exit=_handler,
    )

    return span
