# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

import os
from importlib.metadata import metadata
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from models.file_type import FileType

meta = metadata("h-line")


class Settings(BaseSettings):
    """Основні налаштування програми."""

    @staticmethod
    def get_asset_dir() -> Path:
        """Повертає шлях до директорії з ресурсами."""
        default_assets_dir = Path(__file__).resolve().parent.parent / "assets"
        return Path(os.environ.get("FLET_ASSETS_DIR", default_assets_dir)).resolve()

    name: str = meta["name"]
    version: str = meta["version"]
    license: str = meta["License-Expression"]

    base_url: str = ""
    assets_dir: Path = get_asset_dir()
    templates_dir: Path = assets_dir / "templates"
    template_file_name: str = "application"
    template_file_type: FileType = FileType.DOCX
    output_dir: Path = assets_dir / "output"
    locales_dir: Path = assets_dir / "locales"

    send_to_email: bool = True
    save_to_disk: bool = False

    model_config = SettingsConfigDict(
        env_file=assets_dir / ".env",
        env_prefix="APP__",
        extra="ignore",
    )


settings = Settings()
