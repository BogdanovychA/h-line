# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from datetime import datetime
from typing import Annotated, Union

from pydantic import BaseModel, EmailStr, Field, TypeAdapter
from pydantic_extra_types.phone_numbers import PhoneNumber

email_adapter = TypeAdapter(EmailStr)
phone_adapter = TypeAdapter(PhoneNumber)


class AppealRequest(BaseModel):
    """Модель даних для запиту на звернення."""

    applicant_name: str
    applicant_address: str = ""
    applicant_telephone: Union[Annotated[str, PhoneNumber], str] = ""
    applicant_email: Union[Annotated[str, EmailStr], str] = ""

    applicant_category: str = ""
    applicant_social_status: str = ""

    appeal_content: str

    officer_position: str
    officer_name: str

    created_at: datetime = Field(default_factory=datetime.now)

    def get_context(self) -> dict:
        """Готує контекст даних для використання у шаблонах."""

        context = self.model_dump()

        context['reception_date'] = self.created_at.strftime("%d.%m.%Y")
        context['reception_time'] = self.created_at.strftime("%H:%M:%S")

        return context
