# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from datetime import datetime

import pytest
from pydantic import ValidationError

from models.appeal_request import AppealRequest


@pytest.fixture
def minimal_request():
    return AppealRequest(
        applicant_name="Іваненко Іван Іванович",
        appeal_content="Зміст звернення",
        officer_position="Інспектор",
        officer_name="Петренко Петро",
    )


def test_required_fields_accepted(minimal_request):
    assert minimal_request.applicant_name == "Іваненко Іван Іванович"
    assert minimal_request.appeal_content == "Зміст звернення"
    assert minimal_request.officer_position == "Інспектор"
    assert minimal_request.officer_name == "Петренко Петро"


def test_optional_fields_default_to_empty(minimal_request):
    assert minimal_request.applicant_address == ""
    assert minimal_request.applicant_telephone == ""
    assert minimal_request.applicant_email == ""
    assert minimal_request.applicant_category == ""
    assert minimal_request.applicant_social_status == ""


def test_missing_required_field_raises():
    with pytest.raises(ValidationError):
        AppealRequest(
            appeal_content="Зміст",
            officer_position="Інспектор",
            officer_name="Петренко",
        )


def test_created_at_set_automatically():
    before = datetime.now()
    req = AppealRequest(
        applicant_name="Test",
        appeal_content="Content",
        officer_position="Position",
        officer_name="Officer",
    )
    after = datetime.now()
    assert before <= req.created_at <= after


def test_get_context_contains_all_model_fields(minimal_request):
    ctx = minimal_request.get_context()
    assert "applicant_name" in ctx
    assert "applicant_address" in ctx
    assert "appeal_content" in ctx
    assert "officer_name" in ctx
    assert "officer_position" in ctx
    assert "created_at" in ctx


def test_get_context_formats_date_correctly():
    fixed = datetime(2026, 4, 26, 14, 30, 5)
    req = AppealRequest(
        applicant_name="Test",
        appeal_content="Content",
        officer_position="Position",
        officer_name="Officer",
        created_at=fixed,
    )
    ctx = req.get_context()
    assert ctx["reception_date"] == "26.04.2026"
    assert ctx["reception_time"] == "14:30:05"


def test_get_context_reception_fields_added_separately(minimal_request):
    ctx = minimal_request.get_context()
    assert "reception_date" in ctx
    assert "reception_time" in ctx
