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
from pydantic import ValidationError

from config import app
from models.appeal_request import AppealRequest, email_adapter, phone_adapter
from models.email_errors import EmailFileNotFoundError, EmailSendError
from ui.utils import elements, style

ROUTE = app.settings.base_url + "/application"


def button(page, text: str) -> ft.Button:
    """Створює кнопку для переходу до фіксації звернення"""
    return ft.Button(
        text,
        on_click=lambda: asyncio.create_task(page.push_route(ROUTE)),
    )


async def build_view(
    page: ft.Page,
    box: PandorasBox,
) -> ft.View:
    """Будує вікно для введення даних про звернення громадянина"""

    def _controls_disable():
        """Вимикає кнопки керування під час виконання операції."""

        for block in buttons_block:
            block.disabled = True
            block.update()

    def _controls_enable():
        """Вмикає кнопки керування після завершення операції."""
        for block in buttons_block:
            block.disabled = False
            block.update()

    async def _ok() -> None:

        applicant_name = applicant_name_block.value.strip()
        if not applicant_name:
            message_block.value = box.fluent.get("error-enter-name")
            message_block.update()
            return

        applicant_address = applicant_address_block.value.strip()
        if not applicant_address:
            message_block.value = box.fluent.get("error-enter-address")
            message_block.update()
            return

        applicant_telephone = applicant_telephone_block.value.strip()
        if applicant_telephone:
            try:
                applicant_telephone = phone_adapter.validate_python(applicant_telephone)

            except ValidationError:
                message_block.value = box.fluent.get("error-enter-phone")
                message_block.update()
                return

        applicant_email = applicant_email_block.value.strip()
        if applicant_email:
            try:
                applicant_email = email_adapter.validate_python(applicant_email)

            except ValidationError:
                message_block.value = box.fluent.get("error-enter-email")
                message_block.update()
                return

        appeal_content = appeal_content_block.value.strip()
        if not appeal_content:
            message_block.value = box.fluent.get("error-enter-content")
            message_block.update()
            return

        if (
            applicant_category_switcher.value
            == applicant_category_switcher_options[0].text
        ):
            message_block.value = box.fluent.get("error-select-category")
            message_block.update()
            return

        if (
            applicant_social_status_switcher.value
            == applicant_social_status_switcher_options[0].text
        ):
            message_block.value = box.fluent.get("error-select-social-status")
            message_block.update()
            return

        try:
            appeal = AppealRequest(
                applicant_name=applicant_name,
                applicant_address=applicant_address,
                applicant_telephone=applicant_telephone,
                applicant_email=applicant_email,
                applicant_category=str(applicant_category_switcher.value),
                applicant_social_status=str(applicant_social_status_switcher.value),
                appeal_content=appeal_content,
                officer_position=officer_position,
                officer_name=officer_name,
            )
        except ValidationError as e:
            message_block.value = box.fluent.get("error-create-appeal", error=str(e))
            message_block.update()
            return

        _controls_disable()
        try:

            buffer = await asyncio.to_thread(box.generator.generate_application, appeal)

            if buffer is None:
                message_block.value = box.fluent.get("error-generate-application")
                message_block.update()
                return

            file_name = box.name_creator.create_file_name(box.generator.file_type)

            if box.sender is not None:
                try:
                    await asyncio.to_thread(box.sender.send, buffer, file_name)
                except EmailFileNotFoundError:
                    message_block.value = box.fluent.get("error-create-email")
                    message_block.update()
                    return
                except EmailSendError:
                    message_block.value = box.fluent.get("error-send-email")
                    message_block.update()
                    return

            if box.saver is not None:
                try:
                    box.saver.save(buffer, file_name)
                except PermissionError:
                    message_block.value = box.fluent.get("error-save-file")
                    message_block.update()
                    return

            await box.ga.log_event(
                box.client_id,
                "application_create",
                officer_email=officer_email,
                platform=str(page.platform.value),
            )

            await _clear()
            message_block.value = box.fluent.get("success-appeal-fixed")
            message_block.update()

        finally:
            _controls_enable()

    async def _rerun() -> None:

        await _clear()

        message_block.value = default_message_text
        message_block.update()

    async def _clear():

        for block in applicant_block:
            block.value = ""
            block.update()

        appeal_content_block.value = appeal_content_block_default_value
        appeal_content_block.update()

        applicant_category_switcher.value = applicant_category_switcher_options[0].text
        applicant_category_switcher.update()

        applicant_social_status_switcher.value = (
            applicant_social_status_switcher_options[0].text
        )
        applicant_social_status_switcher.update()

    page.title = box.fluent.get("application-title")

    message_block = ft.Text(
        default_message_text := box.fluent.get("default-message-text"),
        size=style.settings.text_size,
    )

    appeal_content_block_default_value = box.fluent.get("appeal-content-default")

    applicant_block = [
        applicant_name_block := ft.TextField(
            label=box.fluent.get("applicant-name"),
            value="",
            hint_text=box.fluent.get("applicant-name-hint"),
            width=400,
            bgcolor=style.settings.form_bg_color,
            border_color=style.settings.form_border_color,
        ),
        applicant_address_block := ft.TextField(
            label=box.fluent.get("applicant-address"),
            value="",
            hint_text=box.fluent.get("applicant-address-hint"),
            width=400,
            bgcolor=style.settings.form_bg_color,
            border_color=style.settings.form_border_color,
        ),
        applicant_telephone_block := ft.TextField(
            label=box.fluent.get("applicant-telephone"),
            value="",
            hint_text=box.fluent.get("applicant-telephone-hint"),
            keyboard_type=ft.KeyboardType.PHONE,
            width=400,
            bgcolor=style.settings.form_bg_color,
            border_color=style.settings.form_border_color,
        ),
        applicant_email_block := ft.TextField(
            label=box.fluent.get("applicant-email"),
            value="",
            hint_text=box.fluent.get("applicant-email-hint"),
            keyboard_type=ft.KeyboardType.EMAIL,
            width=400,
            bgcolor=style.settings.form_bg_color,
            border_color=style.settings.form_border_color,
        ),
        appeal_content_block := ft.TextField(
            label=box.fluent.get("appeal-content"),
            value=appeal_content_block_default_value,
            hint_text=box.fluent.get("appeal-content-hint"),
            multiline=True,
            min_lines=3,
            max_lines=10,
            width=400,
            bgcolor=style.settings.form_bg_color,
            border_color=style.settings.form_border_color,
        ),
    ]

    def _create_switcher_options(options_keys: list[str]) -> list[ft.DropdownOption]:
        """Створює список опцій для випадаючого меню."""

        options = [
            ft.DropdownOption(text=box.fluent.get("not-selected")),
        ]

        for k in options_keys:
            options.append(ft.DropdownOption(text=box.fluent.get(k)))

        return options

    applicant_category_switcher_options = _create_switcher_options(
        [
            "cat-war-participant",
            "cat-disabled-child",
            "cat-single-mother",
            "cat-mother-heroine",
            "cat-large-family",
            "cat-chernobyl-victim",
            "cat-vpo",
            "cat-chernobyl-liquidator",
            "cat-hero-ukraine",
            "cat-hero-soviet",
            "cat-hero-socialist",
            "cat-child",
            "cat-child-war",
            "cat-disabled-ww2",
            "cat-disabled-war",
            "cat-combat-participant",
            "cat-veteran-military",
            "cat-veteran-labor",
            "cat-disabled-1",
            "cat-disabled-2",
            "cat-disabled-3",
            "cat-other",
        ]
    )

    applicant_category_switcher = ft.Dropdown(
        label=box.fluent.get("applicant-category-label"),
        label_style=ft.TextStyle(size=style.settings.text_size),
        value=applicant_category_switcher_options[0].text,
        options=applicant_category_switcher_options,
        width=400,
        # on_select=,
    )

    applicant_social_status_switcher_options = _create_switcher_options(
        [
            "status-pensioner",
            "status-pensioner-military",
            "status-religious",
            "status-journalist",
            "status-prisoner",
            "status-worker",
            "status-peasant",
            "status-budget-worker",
            "status-civil-servant",
            "status-military",
            "status-entrepreneur",
            "status-unemployed",
            "status-student",
            "status-other",
        ]
    )

    applicant_social_status_switcher = ft.Dropdown(
        label=box.fluent.get("applicant-social-status-label"),
        label_style=ft.TextStyle(size=style.settings.text_size),
        value=applicant_social_status_switcher_options[0].text,
        options=applicant_social_status_switcher_options,
        width=400,
        # on_select=,
    )

    officer_name = box.officer.name
    officer_position = box.officer.position
    officer_email = box.officer.email

    return ft.View(
        route=ROUTE,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            elements.app_bar(box.fluent.get("application-title")),
            ft.Text(""),
            message_block,
            ft.Text(""),
            *applicant_block,
            applicant_category_switcher,
            applicant_social_status_switcher,
            ft.Text(box.fluent.get("required-fields")),
            ft.Text(""),
            ft.Row(
                buttons_block := [
                    ft.IconButton(ft.Icons.REFRESH, on_click=_rerun),
                    ft.IconButton(ft.Icons.DONE_OUTLINE, on_click=_ok),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Text(""),
            ft.Text(
                box.fluent.get(
                    "officer-data",
                    name=officer_name,
                    position=officer_position,
                    email=officer_email,
                )
            ),
            ft.Text(""),
            elements.back_button(page, box.fluent.get("back")),
        ],
    )
