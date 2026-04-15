# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.


class EmailError(Exception):
    """Базовий клас для помилок пошти"""

    pass


class EmailFileNotFoundError(EmailError):
    """Файл для вкладення не знайдено"""

    pass


class EmailSendError(EmailError):
    """Помилка під час SMTP-сесії"""

    pass
