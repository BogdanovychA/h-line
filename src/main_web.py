# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

import uvicorn

from config import server

if __name__ == "__main__":
    uvicorn.run(
        "web.app:web_app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level=(
            server.settings.logging_level.value.lower()
            if server.settings.logging_level
            else "info"
        ),
    )
