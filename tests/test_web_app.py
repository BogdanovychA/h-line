# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

import urllib.parse
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from config import app as app_config
from web.app import web_app


@pytest.fixture
def client():
    return TestClient(web_app)


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "H-Line" in response.text
    assert "htmx.min.js" in response.text
    assert "pico.min.css" in response.text
    assert "client_id" in response.cookies


def test_favicon_endpoints(client):
    for path in ["/favicon.ico", "/favicon.png", "/images/favicon.png"]:
        res = client.get(path)
        assert res.status_code == 200
        assert res.headers["content-type"] == "image/png"


def test_about_and_author_modals(client):
    about_res = client.get("/about-modal")
    assert about_res.status_code == 200
    assert "about-dialog" in about_res.text

    author_res = client.get("/author-modal")
    assert author_res.status_code == 200
    assert "author-dialog" in author_res.text


def test_locale_switch_and_full_translation(client):
    # Switch locale to English via GET
    res_en = client.get("/set-locale?locale=en", follow_redirects=True)
    assert res_en.status_code == 200
    assert "Appeal Registration" in res_en.text
    assert "Generate and send" in res_en.text
    assert "Clear" in res_en.text
    assert "Enter details" in res_en.text
    assert client.cookies.get("locale") == "en"

    # Officer modal in English
    officer_modal_res = client.get("/officer-modal")
    assert officer_modal_res.status_code == 200
    assert "Save" in officer_modal_res.text
    assert "Back" in officer_modal_res.text

    # Switch locale back to Ukrainian via HTMX POST
    res_uk = client.post(
        "/set-locale",
        data={"locale": "uk"},
        headers={"HX-Request": "true"},
    )
    assert res_uk.status_code == 200
    assert res_uk.headers.get("HX-Refresh") == "true"
    assert res_uk.cookies["locale"] == "uk"


def test_officer_modal_and_save(client):
    modal_res = client.get("/officer-modal")
    assert modal_res.status_code == 200
    assert "officer-dialog" in modal_res.text

    # Validation error if empty
    err_res = client.post("/officer", data={"officer_name": ""})
    assert err_res.status_code == 200
    assert "alert-error" in err_res.text

    # Success save
    save_res = client.post(
        "/officer",
        data={
            "officer_name": "Шевченко Тарас Григорович",
            "officer_position": "Директор департаменту",
            "officer_email": "shevchenko@example.com",
        },
    )
    assert save_res.status_code == 200
    assert "Шевченко Тарас Григорович" in save_res.text
    assert 'hx-swap-oob="outerHTML"' in save_res.text
    assert "officer_name" in save_res.cookies


def test_officer_clear(client):
    client.cookies.set("officer_name", urllib.parse.quote("Шевченко Т.Г."))
    client.cookies.set("officer_position", urllib.parse.quote("Директор"))
    client.cookies.set("officer_email", "shevchenko@example.com")

    res = client.post("/officer/clear")
    assert res.status_code == 200
    assert "officer-alert-needed" in res.text
    assert 'hx-swap-oob="outerHTML"' in res.text


def test_form_fields_resets_and_clears_alert(client):
    res = client.get("/form-fields")
    assert res.status_code == 200
    assert 'id="applicant_name"' in res.text
    assert 'id="alert-container" hx-swap-oob="innerHTML"' in res.text


def test_submit_without_officer(client):
    # Without officer cookie, submit should return error alert
    res = client.post(
        "/submit",
        data={
            "applicant_name": "Іванов Іван Іванович",
            "applicant_address": "м. Київ, вул. Хрещатик, 1",
            "appeal_content": "Деякий реальний текст звернення",
            "applicant_category": "Інші категорії",
            "applicant_social_status": "Інші",
        },
    )
    assert res.status_code == 200
    assert "alert-error" in res.text
    assert "Спочатку заповніть дані посадової особи" in res.text


def test_submit_validation_errors(client):
    client.cookies.set("officer_name", urllib.parse.quote("Шевченко Т.Г."))
    client.cookies.set("officer_position", urllib.parse.quote("Директор"))
    client.cookies.set("officer_email", "shevchenko@example.com")

    # Missing applicant name
    res = client.post(
        "/submit",
        data={
            "applicant_name": "",
            "applicant_address": "м. Київ",
            "appeal_content": "Текст",
            "applicant_category": "Інші",
            "applicant_social_status": "Інші",
        },
    )
    assert res.status_code == 200
    assert "alert-error" in res.text

    # Invalid phone
    res = client.post(
        "/submit",
        data={
            "applicant_name": "Іванов Іван",
            "applicant_address": "м. Київ",
            "applicant_telephone": "invalid-phone",
            "appeal_content": "Текст",
            "applicant_category": "Інші",
            "applicant_social_status": "Інші",
        },
    )
    assert res.status_code == 200
    assert "alert-error" in res.text


@patch("web.app.ga_client.log_event")
def test_submit_success(mock_ga, client):
    client.cookies.set("officer_name", urllib.parse.quote("Шевченко Т.Г."))
    client.cookies.set("officer_position", urllib.parse.quote("Директор"))
    client.cookies.set("officer_email", "shevchenko@example.com")

    with patch.object(app_config.settings, "send_to_email", False):
        with patch.object(app_config.settings, "save_to_disk", False):
            res = client.post(
                "/submit",
                data={
                    "applicant_name": "Іванов Іван Іванович",
                    "applicant_address": "м. Київ, вул. Хрещатик, 1",
                    "applicant_telephone": "+380441234567",
                    "applicant_email": "ivanov@example.com",
                    "applicant_category": "Інші категорії",
                    "applicant_social_status": "Інші",
                    "appeal_content": "Прошу розібратися з відключенням світла за адресою...",
                },
            )

    assert res.status_code == 200
    assert "alert-success" in res.text
    assert "form-fields-container" in res.text
