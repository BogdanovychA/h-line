# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Andrii Bogdanovych
# Licensed under the EUPL-1.2 or later
# See the LICENSE file in the project root for more information.

import logging

import httpx

logger = logging.getLogger(__name__)


class MeasurementAPI:
    """Клас для взаємодії з Google Analytics Measurement Protocol."""

    def __init__(self, m10t_id: str, secret_key: str) -> None:
        """Ініціалізує клієнт для відправки подій в Google Analytics."""
        self.id = m10t_id
        self.secret_key = secret_key
        self._is_debug_mode = logging.getLogger().getEffectiveLevel() <= logging.DEBUG

    async def log_event(self, client_id: str, event_name: str, **kwargs) -> bool:
        """Логує подію"""

        suffix = "debug/" if self._is_debug_mode else ""
        base_url = f"https://www.google-analytics.com/{suffix}mp/collect"
        query_params = {"measurement_id": self.id, "api_secret": self.secret_key}

        valid_params = {
            k: v for k, v in kwargs.items() if isinstance(v, (str, int, float, bool))
        }

        payload = {
            "client_id": client_id,
            "events": [
                {
                    "name": event_name,
                    "params": valid_params,
                }
            ],
        }

        try:
            async with httpx.AsyncClient() as client:

                response = await client.post(
                    base_url, params=query_params, json=payload, timeout=5.0
                )

                if self._is_debug_mode:
                    if response.status_code != 200:
                        logger.warning(
                            f"GA debug unexpected status: {response.status_code}"
                        )
                        return False

                    debug_result = response.json()

                    validation_messages = debug_result.get('validationMessages', [])

                    if validation_messages:
                        logger.warning(f"GA validation issues: {validation_messages}")
                        return False
                    else:
                        logger.debug(f"GA event '{event_name}' validated successfully")
                        return True
                else:
                    if response.status_code == 204:
                        logger.info(f"GA event '{event_name}' sent successfully")
                        return True
                    else:
                        logger.warning(
                            f"GA unexpected status {response.status_code} "
                            f"for event '{event_name}'"
                        )
                        return False

        except httpx.TimeoutException:
            logger.error("Analytics request timeout")
            return False

        except httpx.RequestError as e:
            logger.error(f"Analytics request failed: {e}")
            return False

        except Exception as e:
            logger.exception(f"Unexpected analytics error: {e}")
            return False
