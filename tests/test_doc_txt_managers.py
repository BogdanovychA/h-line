# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.doc_manager import DocManager
from core.txt_manager import TxtManager
from models.appeal_request import AppealRequest


class _MockFluent:
    def get(self, key, **kwargs):
        return key


@pytest.fixture
def fluent():
    return _MockFluent()


@pytest.fixture
def sample_request():
    return AppealRequest(
        applicant_name="Іван Іванов",
        appeal_content="Деякий опис проблеми з дорогою.",
        officer_position="Голова громади",
        officer_name="Олександр Петров",
    )


def test_doc_manager_generate_success(fluent, sample_request):
    with patch("core.doc_manager.DocxTemplate") as mock_docx_template_cls:
        mock_doc = MagicMock()
        mock_docx_template_cls.return_value = mock_doc

        manager = DocManager(Path("template.docx"), fluent)
        result = manager.generate_application(sample_request)

        assert isinstance(result, BytesIO)
        mock_docx_template_cls.assert_called_once_with(Path("template.docx"))
        mock_doc.render.assert_called_once_with(sample_request.get_context())
        mock_doc.save.assert_called_once()


def test_doc_manager_generate_failure(fluent, sample_request):
    with patch("core.doc_manager.DocxTemplate") as mock_docx_template_cls:
        mock_docx_template_cls.side_effect = Exception("Rendering failed")

        manager = DocManager(Path("template.docx"), fluent)
        result = manager.generate_application(sample_request)

        assert result is None


def test_txt_manager_generate_success(fluent, sample_request, tmp_path):
    template_file = tmp_path / "template.txt"
    template_file.write_text(
        "Заявник: {{ applicant_name }}\nВміст: {{ appeal_content }}", encoding="utf-8"
    )

    manager = TxtManager(template_file, fluent)
    result = manager.generate_application(sample_request)

    assert isinstance(result, BytesIO)
    content = result.read().decode("utf-8")
    assert "Заявник: Іван Іванов" in content
    assert "Вміст: Деякий опис проблеми з дорогою." in content


def test_txt_manager_generate_failure(fluent, sample_request, tmp_path):
    template_file = tmp_path / "template.txt"
    template_file.write_text("Заявник: {{ non_existent_variable }}", encoding="utf-8")

    manager = TxtManager(template_file, fluent)
    result = manager.generate_application(sample_request)

    assert result is None
