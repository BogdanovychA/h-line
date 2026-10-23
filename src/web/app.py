# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from __future__ import annotations

import asyncio
import logging
import urllib.parse
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Form, Query, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fluent_manager import FluentManager
from measurement_api import MeasurementAPI
from pydantic import ValidationError

from abstract import (
    application_generator,
    application_name_creator,
    application_saver,
    application_sender,
)
from config import app as app_config
from config import google_analytics, server
from core import email_manager, smtp_implementations
from core.doc_manager import DocManager
from core.txt_manager import TxtManager
from models.appeal_request import AppealRequest, email_adapter, phone_adapter
from models.email_errors import EmailSendError
from models.file_type import FileType
from models.logging import EventName
from models.smtp import SMTPProtocol

# Setup logging
logging.basicConfig(
    level=server.settings.logging_level or logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("h_line.web")

# Register template generators
application_generator.GlobalGenerator.register(FileType.DOCX, DocManager)
application_generator.GlobalGenerator.register(FileType.MD, TxtManager)
application_generator.GlobalGenerator.register(FileType.HTML, TxtManager)

# Register SMTP protocols
email_manager.EmailManager.register(
    SMTPProtocol.TLS, smtp_implementations.SMTPSenderTLS
)
email_manager.EmailManager.register(
    SMTPProtocol.SSL, smtp_implementations.SMTPSenderSSL
)

# Supported locales and caching
AVAILABLE_LOCALES = ["uk", "en"]
_fluent_cache: dict[str, FluentManager] = {}


def get_fluent(locale: str | None = None) -> FluentManager:
    """Отримує екземпляр FluentManager для вказаної локалі з кешу."""
    if not locale or locale not in AVAILABLE_LOCALES:
        locale = app_config.settings.start_locale
    if locale not in _fluent_cache:
        _fluent_cache[locale] = FluentManager(
            locales=[locale],
            locales_path=str(app_config.settings.locales_dir),
            default_locale=app_config.settings.default_locale,
        )
    return _fluent_cache[locale]


# Default instance for backward compatibility
fluent_mgr = get_fluent(app_config.settings.start_locale)

# Global services
generator = application_generator.GlobalGenerator(fluent=fluent_mgr)
name_creator = application_name_creator.NameCreator()
file_saver = (
    application_saver.FileSaver(fluent=fluent_mgr)
    if app_config.settings.save_to_disk
    else None
)
ga_client = MeasurementAPI(
    id=google_analytics.settings.id,
    secret_key=google_analytics.settings.secret_key,
    debug=logging.getLogger().getEffectiveLevel() <= logging.DEBUG,
)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
ASSETS_DIR = app_config.settings.assets_dir
ASSETS_IMAGES_DIR = ASSETS_DIR / "images"

CATEGORY_KEYS = [
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

STATUS_KEYS = [
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

web_app = FastAPI(
    title="H-Line Web",
    description="Hotline automation tool for processing citizen appeals",
    version=app_config.settings.version,
)


# Favicon endpoints (registered before mount to avoid static shadow)
@web_app.get("/favicon.ico", include_in_schema=False)
@web_app.get("/favicon.png", include_in_schema=False)
@web_app.get("/images/favicon.png", include_in_schema=False)
async def favicon():
    """Повертає фавіконку застосунку."""
    favicon_path = ASSETS_DIR / "favicon.png"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/png")
    return Response(status_code=404)


# Mount static files
web_app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
if ASSETS_IMAGES_DIR.exists():
    web_app.mount(
        "/images", StaticFiles(directory=str(ASSETS_IMAGES_DIR)), name="images"
    )

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _get_cookie_value(raw_val: str | None) -> str:
    if not raw_val:
        return ""
    try:
        return urllib.parse.unquote(raw_val)
    except Exception:
        return raw_val


def _get_locale(request: Request) -> str:
    cookie_loc = request.cookies.get("locale")
    if cookie_loc in AVAILABLE_LOCALES:
        return cookie_loc
    return app_config.settings.start_locale


def _get_officer_context(request: Request) -> dict[str, str]:
    return {
        "name": _get_cookie_value(request.cookies.get("officer_name")),
        "position": _get_cookie_value(request.cookies.get("officer_position")),
        "email": _get_cookie_value(request.cookies.get("officer_email")),
    }


def _common_context(request: Request) -> dict:
    locale = _get_locale(request)
    fm = get_fluent(locale)
    return {
        "request": request,
        "fluent": fm,
        "current_locale": locale,
        "available_locales": AVAILABLE_LOCALES,
        "officer": _get_officer_context(request),
        "version": app_config.settings.version,
        "license": app_config.settings.license,
        "category_keys": CATEGORY_KEYS,
        "status_keys": STATUS_KEYS,
        "appeal_content_default": fm.get("appeal-content-default"),
    }


@web_app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Головна сторінка веб-інтерфейсу."""
    ctx = _common_context(request)
    client_id = request.cookies.get("client_id")
    response = templates.TemplateResponse(
        request=request, name="index.html", context=ctx
    )

    if not client_id:
        client_id = str(uuid.uuid4())
        response.set_cookie(
            "client_id", client_id, max_age=365 * 24 * 3600, httponly=False
        )

    return response


@web_app.get("/set-locale", response_class=Response)
@web_app.post("/set-locale", response_class=Response)
async def set_locale(
    request: Request,
    locale: Annotated[str, Query()] = "",
):
    """Змінює мову інтерфейсу, зберігає у cookies та оновлює сторінку."""
    if not locale:
        form_data = await request.form()
        locale = str(form_data.get("locale", ""))

    if locale not in AVAILABLE_LOCALES:
        locale = app_config.settings.start_locale

    if "hx-request" in request.headers:
        response = Response(status_code=200)
        response.headers["HX-Refresh"] = "true"
    else:
        response = RedirectResponse(url="/", status_code=303)

    response.set_cookie(
        "locale", locale, max_age=365 * 24 * 3600, path="/", httponly=False
    )
    return response


@web_app.get("/officer-modal", response_class=HTMLResponse)
async def officer_modal(request: Request):
    """Повертає модальне вікно редагування даних посадової особи."""
    ctx = _common_context(request)
    return templates.TemplateResponse(
        request=request, name="partials/officer_modal.html", context=ctx
    )


@web_app.post("/officer", response_class=HTMLResponse)
async def save_officer(
    request: Request,
    officer_name: Annotated[str, Form()] = "",
    officer_position: Annotated[str, Form()] = "",
    officer_email: Annotated[str, Form()] = "",
):
    """Зберігає дані посадової особи у cookies та оновлює шапку."""
    fm = get_fluent(_get_locale(request))
    name = officer_name.strip()
    if not name:
        return templates.TemplateResponse(
            request=request,
            name="partials/alert.html",
            context={
                "status": "error",
                "message": fm.get("error-enter-last-name"),
            },
        )

    position = officer_position.strip()
    if not position:
        return templates.TemplateResponse(
            request=request,
            name="partials/alert.html",
            context={
                "status": "error",
                "message": fm.get("error-enter-position"),
            },
        )

    email = officer_email.strip()
    try:
        email = email_adapter.validate_python(email)
    except ValidationError:
        return templates.TemplateResponse(
            request=request,
            name="partials/alert.html",
            context={
                "status": "error",
                "message": fm.get("error-enter-email"),
            },
        )

    officer_dict = {"name": name, "position": position, "email": email}
    ctx = _common_context(request)
    ctx["officer"] = officer_dict
    ctx["oob"] = True

    # Render badge partial with OOB swap to update the header banner and close the modal
    badge_html = templates.get_template("partials/officer_badge.html").render(ctx)

    html_response = f"""
    {badge_html}
    <div id="modal-container" hx-swap-oob="innerHTML"></div>
    <div id="alert-container" hx-swap-oob="innerHTML"></div>
    """

    res = HTMLResponse(content=html_response)
    cookie_kwargs = {"max_age": 365 * 24 * 3600, "httponly": False, "path": "/"}
    res.set_cookie("officer_name", urllib.parse.quote(name), **cookie_kwargs)
    res.set_cookie("officer_position", urllib.parse.quote(position), **cookie_kwargs)
    res.set_cookie("officer_email", email, **cookie_kwargs)
    return res


@web_app.post("/officer/clear", response_class=HTMLResponse)
async def clear_officer(request: Request):
    """Очищає дані посадової особи у cookies та оновлює шапку."""
    ctx = _common_context(request)
    ctx["officer"] = {"name": "", "position": "", "email": ""}
    ctx["oob"] = True

    badge_html = templates.get_template("partials/officer_badge.html").render(ctx)

    html_response = f"""
    {badge_html}
    <div id="modal-container" hx-swap-oob="innerHTML"></div>
    <div id="alert-container" hx-swap-oob="innerHTML"></div>
    """

    res = HTMLResponse(content=html_response)
    res.delete_cookie("officer_name", path="/")
    res.delete_cookie("officer_position", path="/")
    res.delete_cookie("officer_email", path="/")
    return res


@web_app.get("/form-fields", response_class=HTMLResponse)
async def form_fields(request: Request):
    """Повертає чисті поля форми для скидання стану та очищає контейнер сповіщень."""
    ctx = _common_context(request)
    fields_html = templates.get_template("partials/form_fields.html").render(ctx)
    response_html = f"""
    {fields_html}
    <div id="alert-container" hx-swap-oob="innerHTML"></div>
    """
    return HTMLResponse(content=response_html)


@web_app.get("/about-modal", response_class=HTMLResponse)
async def about_modal(request: Request):
    """Повертає модальне вікно з інформацією про застосунок."""
    ctx = _common_context(request)
    return templates.TemplateResponse(
        request=request, name="partials/about_modal.html", context=ctx
    )


@web_app.get("/author-modal", response_class=HTMLResponse)
async def author_modal(request: Request):
    """Повертає модальне вікно з інформацією про автора."""
    ctx = _common_context(request)
    return templates.TemplateResponse(
        request=request, name="partials/author_modal.html", context=ctx
    )


@web_app.post("/submit", response_class=HTMLResponse)
async def submit_appeal(
    request: Request,
    applicant_name: Annotated[str, Form()] = "",
    applicant_address: Annotated[str, Form()] = "",
    applicant_telephone: Annotated[str, Form()] = "",
    applicant_email: Annotated[str, Form()] = "",
    applicant_category: Annotated[str, Form()] = "",
    applicant_social_status: Annotated[str, Form()] = "",
    appeal_content: Annotated[str, Form()] = "",
):
    """Обробляє надсилання форми звернення громадянина через HTMX."""
    fm = get_fluent(_get_locale(request))
    officer = _get_officer_context(request)
    if not (officer["name"] and officer["position"] and officer["email"]):
        return templates.TemplateResponse(
            request=request,
            name="partials/alert.html",
            context={
                "status": "error",
                "message": fm.get("error-fill-officer-first"),
            },
        )

    # 1. Validation
    name = applicant_name.strip()
    if not name:
        return templates.TemplateResponse(
            request=request,
            name="partials/alert.html",
            context={
                "status": "error",
                "message": fm.get("error-enter-name"),
            },
        )

    address = applicant_address.strip()
    if not address:
        return templates.TemplateResponse(
            request=request,
            name="partials/alert.html",
            context={
                "status": "error",
                "message": fm.get("error-enter-address"),
            },
        )

    telephone = applicant_telephone.strip()
    if telephone:
        try:
            telephone = str(phone_adapter.validate_python(telephone))
        except ValidationError:
            return templates.TemplateResponse(
                request=request,
                name="partials/alert.html",
                context={
                    "status": "error",
                    "message": fm.get("error-enter-phone"),
                },
            )

    email = applicant_email.strip()
    if email:
        try:
            email = str(email_adapter.validate_python(email))
        except ValidationError:
            return templates.TemplateResponse(
                request=request,
                name="partials/alert.html",
                context={
                    "status": "error",
                    "message": fm.get("error-enter-email"),
                },
            )

    content = appeal_content.strip()
    default_content = fm.get("appeal-content-default").strip()
    if not content or content == default_content:
        return templates.TemplateResponse(
            request=request,
            name="partials/alert.html",
            context={
                "status": "error",
                "message": fm.get("error-enter-content"),
            },
        )

    if not applicant_category:
        return templates.TemplateResponse(
            request=request,
            name="partials/alert.html",
            context={
                "status": "error",
                "message": fm.get("error-select-category"),
            },
        )

    if not applicant_social_status:
        return templates.TemplateResponse(
            request=request,
            name="partials/alert.html",
            context={
                "status": "error",
                "message": fm.get("error-select-social-status"),
            },
        )

    # 2. Build AppealRequest
    try:
        appeal = AppealRequest(
            applicant_name=name,
            applicant_address=address,
            applicant_telephone=telephone,
            applicant_email=email,
            applicant_category=applicant_category,
            applicant_social_status=applicant_social_status,
            appeal_content=content,
            officer_position=officer["position"],
            officer_name=officer["name"],
        )
    except ValidationError as e:
        return templates.TemplateResponse(
            request=request,
            name="partials/alert.html",
            context={
                "status": "error",
                "message": fm.get("error-create-appeal", error=str(e)),
            },
        )

    # 3. Generate file
    try:
        doc_generator = application_generator.GlobalGenerator(fluent=fm)
        buffer = await asyncio.to_thread(doc_generator.generate_application, appeal)
        if buffer is None:
            return templates.TemplateResponse(
                request=request,
                name="partials/alert.html",
                context={
                    "status": "error",
                    "message": fm.get("error-generate-application"),
                },
            )

        file_name = name_creator.create_file_name(doc_generator.file_type)

        # 4. Email sender
        if app_config.settings.send_to_email:
            try:
                sender = application_sender.EmailSender(
                    fluent=fm, cc_recipients=[officer["email"]]
                )
                await asyncio.to_thread(sender.send, buffer, file_name)
            except EmailSendError:
                logger.exception("Error sending email")
                return templates.TemplateResponse(
                    request=request,
                    name="partials/alert.html",
                    context={
                        "status": "error",
                        "message": fm.get("error-send-email"),
                    },
                )

        # 5. File saver
        if app_config.settings.save_to_disk:
            try:
                saver = application_saver.FileSaver(fluent=fm)
                await asyncio.to_thread(saver.save, buffer, file_name)
            except PermissionError:
                logger.exception("Error saving file to disk")
                return templates.TemplateResponse(
                    request=request,
                    name="partials/alert.html",
                    context={
                        "status": "error",
                        "message": fm.get("error-save-file"),
                    },
                )

        # 6. Analytics
        client_id = request.cookies.get("client_id") or str(uuid.uuid4())
        await ga_client.log_event(
            client_id,
            EventName.APPLICATION_CREATE,
            officer_email=officer["email"],
            platform="web",
        )

    except Exception as e:
        logger.exception("Unexpected error processing appeal")
        return templates.TemplateResponse(
            request=request,
            name="partials/alert.html",
            context={
                "status": "error",
                "message": fm.get("unexpected-error", error=str(e)),
            },
        )

    # 7. Success! Render success alert + OOB swap to reset form fields
    ctx = _common_context(request)
    form_reset_html = templates.get_template("partials/form_fields.html").render(ctx)

    success_msg = fm.get("success-appeal-fixed")
    response_html = f"""
    <div class="alert-success" role="alert">
      ✅ {success_msg}
    </div>
    <div id="form-fields-container" hx-swap-oob="innerHTML">
      {form_reset_html}
    </div>
    """
    return HTMLResponse(content=response_html)
