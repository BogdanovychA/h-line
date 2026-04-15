# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

import asyncio
import logging
import uuid

import flet as ft
from flet_storage import FletStorage
from pydantic import ValidationError

from abstract import (
    application_generator,
    application_name_creator,
    application_saver,
    application_sender,
)
from config import app, google_analytics, server
from core import email_manager, smtp_implementations
from core.doc_manager import DocManager
from core.txt_manager import TxtManager
from models.appeal_request import email_adapter
from models.file_type import FileType
from models.smtp import SMTPProtokol
from ui.routes import about, application, author, error404, root
from ui.utils import elements, style
from ui.utils.models import Officer, PandorasBox
from utils.measurement_api import MeasurementAPI

logging.basicConfig(
    level=server.settings.logging_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def build_main_view(
    page: ft.Page,
    box: PandorasBox,
) -> ft.View:
    """Будує головне вікно для введення даних про посадову особу"""

    async def _ok(event: ft.Event) -> None:
        """Обробник натискання кнопки підтвердження даних посадової особи"""

        name = officer_name_block.value.strip()
        if not name:
            message_block.value = "Введіть прізвище"
            event.page.update()
            return
        if box.officer.name != name:
            box.officer.name = name
            try:
                await box.storage.set("officer_name", name)
            except RuntimeError:
                logger.exception("Помилка при записі officer_name")

        position = officer_position_block.value.strip()
        if not position:
            message_block.value = "Введіть посаду"
            event.page.update()
            return
        if box.officer.position != position:
            box.officer.position = position
            try:
                await box.storage.set("officer_position", position)
            except RuntimeError:
                logger.exception("Помилка при записі officer_position")

        try:
            email = email_adapter.validate_python(officer_email_block.value)
            if box.officer.email != email:
                box.officer.email = email
                try:
                    await box.storage.set("officer_email", email)
                except RuntimeError:
                    logger.exception("Помилка при записі officer_email")

        except ValidationError:
            message_block.value = "Введіть коректний email"
            event.page.update()
            return

        message_block.value = "Вхід..."

        if app.settings.send_to_email:
            box.sender = application_sender.EmailSender(cc_recipients=[email])

        event.page.update()
        await page.push_route(application.ROUTE)

    async def _rerun(event: ft.Event) -> None:
        """Скидає налаштування та очищує поля вводу для посадової особи"""

        keys_list = await box.storage.get_keys()
        keys_to_remove = [k for k in keys_list if k != "client_id"]
        for key in keys_to_remove:
            await box.storage.remove(key)

        box.officer = Officer()

        for block in officer_block:
            block.value = ""

        message_block.value = default_message_text

        event.page.update()

    page.title = root.TITLE

    message_block = ft.Text(
        default_message_text := "Введіть ваші ПІБ, посаду та електронну пошту",
        size=style.settings.text_size,
    )

    officer_block = [
        officer_name_block := ft.TextField(
            label="Ваші ПІБ",
            value=box.officer.name,
            hint_text="ПІБ: Шевченко Тарас Григорович",
            width=350,
            bgcolor=style.settings.form_bg_color,
            border_color=style.settings.form_border_color,
        ),
        officer_position_block := ft.TextField(
            label="Ваша посада",
            value=box.officer.position,
            hint_text="Посада (коротко): головний спеціаліст",
            width=350,
            bgcolor=style.settings.form_bg_color,
            border_color=style.settings.form_border_color,
        ),
        officer_email_block := ft.TextField(
            label="Ваша електронна пошта",
            value=box.officer.email,
            hint_text="Email: ShevchenkoT@sies.gov.ua",
            width=350,
            bgcolor=style.settings.form_bg_color,
            border_color=style.settings.form_border_color,
        ),
    ]

    return ft.View(
        route=root.ROUTE,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            elements.app_bar(root.TITLE),
            # ft.Text(""),
            ft.Image(
                src="/images/logo-sies-317x312.png",
                width=200,
                height=200,
            ),
            ft.Text(""),
            message_block,
            ft.Text(""),
            *officer_block,
            ft.Text(""),
            ft.Row(
                [
                    ft.IconButton(ft.Icons.REFRESH, on_click=_rerun),
                    ft.IconButton(ft.Icons.DONE_OUTLINE, on_click=_ok),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Text(""),
            ft.Row(
                controls=[
                    author.button(page),
                    about.button(page),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
    )


async def main(page: ft.Page):
    """Головна функція ініціалізації та запуску Flet-застосунку"""

    async def route_change():
        """Обробляє зміну маршруту сторінки"""

        await box.ga.log_event(
            box.client_id,
            "route_change",
            page_path=page.route,
            platform=str(page.platform.value),
        )

        page.views.clear()
        page.views.append(await build_main_view(page, box))

        match page.route:
            case application.ROUTE:
                page.views.append(await application.build_view(page, box))
            case author.ROUTE:
                page.views.append(author.build_view(page))
            case about.ROUTE:
                page.views.append(about.build_view(page))
            case _:
                if page.route != root.ROUTE:
                    page.views.append(error404.build_view(page))

        page.update()

    async def view_pop(e):
        """Обробляє повернення на попередню сторінку"""
        if e.view is not None:
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.title = root.TITLE
    page.theme_mode = ft.ThemeMode.DARK
    page.route = root.ROUTE

    application_generator.GlobalGenerator.register(FileType.DOCX, DocManager)
    application_generator.GlobalGenerator.register(FileType.MD, TxtManager)
    application_generator.GlobalGenerator.register(FileType.HTML, TxtManager)

    email_manager.EmailManager.register(
        SMTPProtokol.TLS, smtp_implementations.SMTPSenderTLS
    )
    email_manager.EmailManager.register(
        SMTPProtokol.SSL, smtp_implementations.SMTPSenderSSL
    )

    box = PandorasBox(
        storage=FletStorage(app.settings.name),
        generator=application_generator.GlobalGenerator(),
        ga=MeasurementAPI(
            m10t_id=google_analytics.settings.id,
            secret_key=google_analytics.settings.secret_key,
        ),
        name_creator=application_name_creator.NameCreator(),
        saver=application_saver.FileSaver() if app.settings.save_to_disk else None,
    )

    await asyncio.sleep(0.2)

    try:
        box.client_id = await box.storage.get_or_default("client_id", str(uuid.uuid4()))
        if not await box.storage.contains_key("client_id"):
            await box.storage.set("client_id", box.client_id)
    except RuntimeError:
        logger.exception("Помилка при зчитуванні даних про client_id")
        box.client_id = str(uuid.uuid4())

    try:
        box.officer.name = await box.storage.get_or_default("officer_name", "")
        box.officer.position = await box.storage.get_or_default("officer_position", "")
        box.officer.email = await box.storage.get_or_default("officer_email", "")
    except RuntimeError:
        logger.exception("Помилка при зчитуванні даних про офіцера")
        (
            box.officer.name,
            box.officer.position,
            box.officer.email,
        ) = ("", "", "")

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    await route_change()
