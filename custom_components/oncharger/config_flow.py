"""Config flow for Oncharger integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import (
    CLOUD,
    CONNECTION_TYPE,
    DEVICE_NAME,
    DOMAIN,
    IP_ADDRESS,
    LOCAL,
    PASSWORD,
    USERNAME,
)
from .oncharger import Oncharger
from .coordinator import InvalidAuth, OnchargerCoordinator

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONNECTION_TYPE, default=LOCAL): vol.In((LOCAL, CLOUD)),
        vol.Required(DEVICE_NAME, default=DOMAIN.capitalize()): str,
    }
)

LOCAL_SCHEMA = vol.Schema(
    {
        vol.Required(IP_ADDRESS): str,
        vol.Required(USERNAME): str,
        vol.Required(PASSWORD): str,
    }
)

CLOUD_SCHEMA = vol.Schema(
    {
        vol.Required(USERNAME): str,
        vol.Required(PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """

    oncharger = Oncharger(data)
    coordinator = OnchargerCoordinator(oncharger, hass)
    await coordinator.async_validate_input()

    return {"title": data[DEVICE_NAME]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Oncharger."""

    VERSION = 1

    def __init__(self) -> None:
        """Start the Wallbox config flow."""
        self._device_name = None

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=USER_SCHEMA, errors={}
            )

        self._device_name = user_input[DEVICE_NAME]
        if user_input[CONNECTION_TYPE] == LOCAL:
            return await self.async_step_local()
        return await self.async_step_cloud()

    async def async_step_local(self, user_input=None):
        """Set up local device details."""

        return await self._async_step_device(
            step_id=LOCAL,
            data_schema=LOCAL_SCHEMA,
            user_input=user_input,
        )

    async def async_step_cloud(self, user_input=None):
        """Set up cloud device details."""

        return await self._async_step_device(
            step_id=CLOUD, data_schema=CLOUD_SCHEMA, user_input=user_input
        )

    async def _async_step_device(self, step_id=None, data_schema=None, user_input=None):
        """Set up device details."""
        if user_input is None:
            return self.async_show_form(step_id=step_id, data_schema=data_schema)

        user_input[DEVICE_NAME] = self._device_name
        errors = {}

        try:
            await self.async_set_unique_id(user_input[DEVICE_NAME])
            self._abort_if_unique_id_configured()

            info = await validate_input(self.hass, user_input)
            return self.async_create_entry(title=info["title"], data=user_input)
        except ConnectionError:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception as exception_error:  # pylint: disable=broad-except
            _LOGGER.exception(f"Unexpected exception {exception_error}")
            errors["base"] = "unknown"

        data_schema = self.add_suggested_values_to_schema(data_schema, user_input)
        return self.async_show_form(
            step_id=step_id, data_schema=data_schema, errors=errors
        )
