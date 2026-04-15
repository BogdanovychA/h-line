# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

import flet as ft

from config import app
from ui.main import main

if __name__ == "__main__":
    ft.run(main, assets_dir=app.settings.assets_dir)
