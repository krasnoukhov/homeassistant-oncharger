"""DataUpdateCoordinator for the Oncharger integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .oncharger import Forbidden, Oncharger
from .const import (
    DOMAIN,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class OnchargerCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Oncharger Coordinator class."""

    def __init__(self, oncharger: Oncharger, hass: HomeAssistant) -> None:
        """Initialize."""
        self._oncharger = oncharger

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    def _validate(self) -> None:
        """Validate using Oncharger API."""
        try:
            return self._oncharger.get_config()
        except Forbidden as forbidden_error:
            raise InvalidAuth from forbidden_error

    async def async_validate_input(self) -> None:
        """Get new sensor data for Oncharger component."""
        return await self.hass.async_add_executor_job(self._validate)

    def _get_data(self) -> dict[str, Any]:
        """Get new sensor data for Oncharger component."""
        try:
            config: dict[str, Any] = self._oncharger.get_config()
            status: dict[str, Any] = self._oncharger.get_status()
            data = config | status

            # NOTE: cloud is amp, local is amp1
            if data.get("amp") is None:
                data["amp"] = data["amp1"]
            # NOTE: 3 phase for some reason does not have volt1 but have volt
            if data.get("volt1") is None:
                data["volt1"] = data["volt"]

            return data
        except Forbidden as forbidden_error:
            raise InvalidAuth from forbidden_error
        except ConnectionError as http_error:
            raise UpdateFailed from http_error

    async def _async_update_data(self) -> dict[str, Any]:
        """Get new sensor data for Oncharger component."""
        return await self.hass.async_add_executor_job(self._get_data)

    def _set_charging_current(self, charging_current: float) -> None:
        """Set maximum charging current for Oncharger."""
        try:
            self._oncharger.set_max_charging_current(charging_current)
        except Forbidden as forbidden_error:
            raise InvalidAuth from forbidden_error

    async def async_set_charging_current(self, charging_current: float) -> None:
        """Set maximum charging current for Oncharger."""
        await self.hass.async_add_executor_job(
            self._set_charging_current, charging_current
        )
        await self.async_request_refresh()

    def _set_lock_unlock(self, lock: bool) -> None:
        """Set Oncharger to locked or unlocked."""
        try:
            self._oncharger.set_lock_unlock(lock)
        except Forbidden as forbidden_error:
            raise InvalidAuth from forbidden_error

    async def async_set_lock_unlock(self, lock: bool) -> None:
        """Set Oncharger to locked or unlocked."""
        await self.hass.async_add_executor_job(self._set_lock_unlock, lock)
        await self.async_request_refresh()

    def _set_boost_config(self, *args) -> None:
        """Set Oncharger boost config."""
        try:
            self._oncharger.set_boost_config(*args)
        except Forbidden as forbidden_error:
            raise InvalidAuth from forbidden_error

    async def async_set_boost_config(self, *args) -> None:
        """Set Oncharger boost config."""
        await self.hass.async_add_executor_job(self._set_boost_config, *args)
        await self.async_request_refresh()


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
