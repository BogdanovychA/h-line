# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

import flet as ft
from pydantic import BaseModel


class Settings(BaseModel):
    """Налаштування стилів та візуального відображення елементів інтерфейсу"""

    title_size: int = 24
    text_size: int = 20

    link_color: ft.Colors = ft.Colors.PRIMARY
    form_border_color: ft.Colors = ft.Colors.PRIMARY
    form_bg_color: ft.Colors = ft.Colors.SURFACE_CONTAINER


settings = Settings()
