# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

from pydantic_settings import BaseSettings, SettingsConfigDict

from config import app
from models.logging import LoggingLevel


class Settings(BaseSettings):
    """Налаштування сервера та логування."""

    logging_level: LoggingLevel | None = None

    model_config = SettingsConfigDict(
        env_file=app.settings.assets_dir / ".env",
        env_prefix="SERVER__",
        extra="ignore",
    )


settings = Settings()
