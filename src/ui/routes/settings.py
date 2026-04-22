# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.utils.models import PandorasBox

import flet as ft
from fluent_manager import FluentManager

from config import app
from ui.utils import elements, style

ROUTE = app.settings.base_url + "/settings"


def button(page, text: str) -> ft.Button:
    """Створює кнопку для переходу до екрану налаштувань"""
    return ft.Button(
        text,
        on_click=lambda: asyncio.create_task(page.push_route(ROUTE)),
    )


async def build_view(
    page: ft.Page,
    box: PandorasBox,
) -> ft.View:
    """Будує вікно для введення даних про звернення громадянина"""

    async def _lang_switch(event: ft.Event) -> None:
        """Обробник перемикача мови"""

        new_locale = lang_switcher.value

        box.fluent = FluentManager(
            locales=[new_locale],
            locales_path=str(app.settings.locales_dir),
            default_locale=app.settings.default_locale,
        )

        event.page.views.clear()
        event.page.views.append(await build_view(page, box))

    page.title = box.fluent.get("settings-title")

    def _create_lang_switcher_options() -> list[ft.DropdownOption]:
        options = []
        for language in box.fluent.languages:
            options.append(ft.DropdownOption(key=language, text=language.upper()))
        return options

    lang_switcher = ft.Dropdown(
        label=box.fluent.get("settings-lang-switch"),
        label_style=ft.TextStyle(size=style.settings.text_size),
        value=box.fluent.locales[0],
        options=_create_lang_switcher_options(),
        on_select=_lang_switch,
    )

    return ft.View(
        route=ROUTE,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            elements.app_bar(box.fluent.get("settings-title"), page),
            ft.Text(""),
            ft.Text(box.fluent.get("settings-title"), size=style.settings.text_size),
            ft.Text(""),
            lang_switcher,
            ft.Text(""),
            elements.back_button(page, box.fluent.get("back")),
        ],
    )
