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

TITLE = "Фіксація звернення"

ROUTE = app.settings.base_url + "/application"


def button(page) -> ft.Button:
    """Створює кнопку для переходу до фіксації звернення"""
    return ft.Button(
        TITLE,
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
            message_block.value = "Введіть ПІБ громадянина"
            message_block.update()
            return

        applicant_address = applicant_address_block.value.strip()
        if not applicant_address:
            message_block.value = "Введіть адресу громадянина"
            message_block.update()
            return

        applicant_telephone = applicant_telephone_block.value.strip()
        if applicant_telephone:
            try:
                applicant_telephone = phone_adapter.validate_python(applicant_telephone)

            except ValidationError:
                message_block.value = "Введіть коректний телефон"
                message_block.update()
                return

        applicant_email = applicant_email_block.value.strip()
        if applicant_email:
            try:
                applicant_email = email_adapter.validate_python(applicant_email)

            except ValidationError:
                message_block.value = "Введіть коректний email"
                message_block.update()
                return

        appeal_content = appeal_content_block.value.strip()
        if not appeal_content:
            message_block.value = "Введіть текст звернення"
            message_block.update()
            return

        if (
            applicant_category_switcher.value
            == applicant_category_switcher_options[0].text
        ):
            message_block.value = "Оберіть категорію"
            message_block.update()
            return

        if (
            applicant_social_status_switcher.value
            == applicant_social_status_switcher_options[0].text
        ):
            message_block.value = "Оберіть соціальний стан"
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
            message_block.value = f"Помилка при створенні звернення: {str(e)}"
            message_block.update()
            return

        _controls_disable()
        try:

            buffer = await asyncio.to_thread(box.generator.generate_application, appeal)

            if buffer is None:
                message_block.value = "Помилка при створенні звернення..."
                message_block.update()
                return

            file_name = box.name_creator.create_file_name(box.generator.file_type)

            if box.sender is not None:
                try:
                    await asyncio.to_thread(box.sender.send, buffer, file_name)
                except EmailFileNotFoundError:
                    message_block.value = "Помилка при створенні email..."
                    message_block.update()
                    return
                except EmailSendError:
                    message_block.value = "Помилка при надсиланні email..."
                    message_block.update()
                    return

            if box.saver is not None:
                try:
                    box.saver.save(buffer, file_name)
                except PermissionError:
                    message_block.value = "Помилка при збереженні файлу..."
                    message_block.update()
                    return

            await box.ga.log_event(
                box.client_id,
                "application_create",
                officer_email=officer_email,
                platform=str(page.platform.value),
            )

            await _clear()
            message_block.value = "Звернення зафіксовано! Можна фіксувати наступне."
            message_block.update()

        finally:
            _controls_enable()

    async def _rerun() -> None:

        await _clear()

        appeal_content_block.value = appeal_content_block_default_value
        appeal_content_block.update()

        message_block.value = default_message_text
        message_block.update()

    async def _clear():

        for block in applicant_block:
            block.value = ""
            block.update()

        applicant_category_switcher.value = applicant_category_switcher_options[0].text
        applicant_category_switcher.update()

        applicant_social_status_switcher.value = (
            applicant_social_status_switcher_options[0].text
        )
        applicant_social_status_switcher.update()

    page.title = TITLE

    message_block = ft.Text(
        default_message_text := "Введіть інформацію",
        size=style.settings.text_size,
    )

    appeal_content_block_default_value = """Суть звернення:

Чи звертався громадянин до ОСР, місцевої влади, керуючої компанії тощо:

Якщо так, який результат:

Що громадянин просить у Держенергонагляду:
"""

    applicant_block = [
        applicant_name_block := ft.TextField(
            label="ПІБ громадянина *",
            value="",
            hint_text="Прізвище, ім'я, по батькові",
            width=400,
            bgcolor=style.settings.form_bg_color,
            border_color=style.settings.form_border_color,
        ),
        applicant_address_block := ft.TextField(
            label="Адреса проживання громадянина *",
            value="",
            hint_text="01001, м. Київ, вулиця Хрещатик, буд. 1",
            width=400,
            bgcolor=style.settings.form_bg_color,
            border_color=style.settings.form_border_color,
        ),
        applicant_telephone_block := ft.TextField(
            label="Номер телефону громадянина",
            value="",
            hint_text="+380441234567",
            keyboard_type=ft.KeyboardType.PHONE,
            width=400,
            bgcolor=style.settings.form_bg_color,
            border_color=style.settings.form_border_color,
        ),
        applicant_email_block := ft.TextField(
            label="Електронна пошта громадянина",
            value="",
            hint_text="example@domain.com",
            keyboard_type=ft.KeyboardType.EMAIL,
            width=400,
            bgcolor=style.settings.form_bg_color,
            border_color=style.settings.form_border_color,
        ),
        appeal_content_block := ft.TextField(
            label="Зміст звернення громадянина",
            value=appeal_content_block_default_value,
            hint_text="Опишіть суть звернення громадянина...",
            multiline=True,
            min_lines=3,
            max_lines=10,
            width=400,
            bgcolor=style.settings.form_bg_color,
            border_color=style.settings.form_border_color,
        ),
    ]

    def _create_switcher_options(options_value: list[str]) -> list[ft.DropdownOption]:
        """Створює список опцій для випадаючого меню."""

        options = [
            ft.DropdownOption(text="Не обрано"),
        ]

        for o in options_value:
            options.append(ft.DropdownOption(text=o))

        return options

    applicant_category_switcher_options = _create_switcher_options(
        [
            "Учасник війни",
            "Дитина з інвалідністю",
            "Одинока мати",
            "Мати-героїня",
            "Багатодітна сім'я",
            "Особа, що потерпіла від Чорнобильської катастрофи",
            "Внутрішньо переміщена особа",
            "Учасник ліквідації наслідків аварії на Чорнобильській АЕС",
            "Герой України",
            "Герой Радянського Союзу",
            "Герой Соціалістичної Праці",
            "Дитина",
            "Дитина війни",
            "Особа з інвалідністю внаслідок Другої світової війни",
            "Особа з інвалідністю внаслідок війни",
            "Учасник бойових дій",
            "Ветеран військової служби",
            "Ветеран праці",
            "Особа з інвалідністю I групи",
            "Особа з інвалідністю II групи",
            "Особа з інвалідністю III групи",
            "Інші категорії",
        ]
    )

    applicant_category_switcher = ft.Dropdown(
        label="Категорія громадянина *",
        label_style=ft.TextStyle(size=style.settings.text_size),
        value=applicant_category_switcher_options[0].text,
        options=applicant_category_switcher_options,
        width=400,
        # on_select=,
    )

    applicant_social_status_switcher_options = _create_switcher_options(
        [
            "Пенсіонер",
            "Пенсіонер з числа військовослужбовців",
            "Служитель релігійної організації",
            "Журналіст",
            "Особа, що позбавлена волі; особа, воля якої обмежена",
            "Робітник",
            "Селянин",
            "Працівник бюджетної сфери",
            "Державний службовець",
            "Військовослужбовець",
            "Підприємець",
            "Безробітний",
            "Учень, студент",
            "Інші",
        ]
    )

    applicant_social_status_switcher = ft.Dropdown(
        label="Соціальний стан громадянина *",
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
            elements.app_bar(TITLE),
            ft.Text(""),
            message_block,
            ft.Text(""),
            *applicant_block,
            applicant_category_switcher,
            applicant_social_status_switcher,
            ft.Text("* — обов'язкові поля"),
            ft.Text(""),
            ft.Row(
                buttons_block := [
                    ft.IconButton(ft.Icons.REFRESH, on_click=_rerun),
                    ft.IconButton(ft.Icons.DONE_OUTLINE, on_click=_ok),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Text(""),
            ft.Text(f"Ваші дані: {officer_name}; {officer_position}; {officer_email}"),
            ft.Text(""),
            elements.back_button(page),
        ],
    )
