# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from pydantic_settings import BaseSettings, SettingsConfigDict

from config import app
from models.smtp import SMTPProtokol


class Settings(BaseSettings):
    """
    Налаштування відправника електронної пошти.
    """

    server: str | None = None
    port: int | None = None
    email: str | None = None
    password: str | None = None
    protokol: SMTPProtokol | None = None

    model_config = SettingsConfigDict(
        env_file=app.settings.assets_dir / ".env",
        env_prefix="EMAIL_SENDER__",
        extra="ignore",
    )


settings = Settings()
