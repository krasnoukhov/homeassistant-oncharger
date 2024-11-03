"""Config flow for Oncharger integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import AbortFlow
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_DOMAIN,
    Platform,
)
from homeassistant.helpers.selector import selector
import homeassistant.helpers.config_validation as cv

from .const import (
    ATTR_ENTITY,
    CLOUD,
    CONNECTION_TYPE,
    CHARGER_NAME_KEY,
    DEVICE_NAME,
    DEVICE_TYPE,
    DOMAIN,
    IP_ADDRESS,
    LOCAL,
    PASSWORD,
    PHASE_CURRENT_ENTITY,
    PHASE_MAX_LOAD_MIN,
    PHASE_MAX_LOAD,
    SINGLE_PHASE,
    THREE_PHASE,
    USERNAME,
)
from .oncharger import Oncharger
from .coordinator import InvalidAuth, OnchargerCoordinator

_LOGGER = logging.getLogger(__name__)

BOOST_FIELDS = {
    vol.Optional(PHASE_CURRENT_ENTITY): selector(
        {
            ATTR_ENTITY: {
                ATTR_DEVICE_CLASS: SensorDeviceClass.CURRENT,
                ATTR_DOMAIN: Platform.SENSOR,
            }
        }
    ),
    vol.Optional(PHASE_MAX_LOAD, default=16): vol.All(
        vol.Coerce(int), vol.Range(min=PHASE_MAX_LOAD_MIN)
    ),
}
LOGIN_FIELDS = {
    vol.Required(USERNAME): cv.string,
    vol.Required(PASSWORD): cv.string,
}

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONNECTION_TYPE, default=LOCAL): vol.In((LOCAL, CLOUD)),
        vol.Required(DEVICE_TYPE, default=SINGLE_PHASE): vol.In((SINGLE_PHASE, THREE_PHASE)),
        vol.Required(DEVICE_NAME, default=DOMAIN.capitalize()): cv.string,
    }
)
LOCAL_SCHEMA = vol.Schema(
    {
        vol.Required(IP_ADDRESS): cv.string,
        **LOGIN_FIELDS,
        **BOOST_FIELDS,
    }
)
CLOUD_SCHEMA = vol.Schema(LOGIN_FIELDS)
OPTIONS_SCHEMA = vol.Schema(BOOST_FIELDS)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """

    oncharger = Oncharger(data)
    coordinator = OnchargerCoordinator(oncharger, hass)
    coordinator_data = await coordinator.async_validate_input()

    return {"title": data[DEVICE_NAME], "unique_id": coordinator_data[CHARGER_NAME_KEY]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Oncharger."""

    VERSION = 1

    def __init__(self) -> None:
        """Start the Wallbox config flow."""
        self._device_name = None
        self._device_type = None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=USER_SCHEMA, errors={}
            )

        self._device_name = user_input[DEVICE_NAME]
        self._device_type = user_input[DEVICE_TYPE]

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
        user_input[DEVICE_TYPE] = self._device_type

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
            options = dict((str(d), user_input.pop(d, None)) for d in BOOST_FIELDS)

            await self.async_set_unique_id(f"{info['unique_id']}-{step_id}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=info["title"], data=user_input, options=options
            )
        except ConnectionError:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except AbortFlow as abort_flow_error:
            errors["base"] = abort_flow_error.reason
        except Exception as exception_error:  # pylint: disable=broad-except
            _LOGGER.exception(f"Unexpected exception {exception_error}")
            errors["base"] = "unknown"

        data_schema = self.add_suggested_values_to_schema(data_schema, user_input)
        return self.async_show_form(
            step_id=step_id, data_schema=data_schema, errors=errors
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Oncharger."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Manage the options."""
        data_schema = self.add_suggested_values_to_schema(
            OPTIONS_SCHEMA, self.config_entry.options
        )

        if user_input is None:
            return self.async_show_form(
                step_id="init",
                data_schema=(
                    data_schema if self.config_entry.data.get(IP_ADDRESS) else None
                ),
            )

        return self.async_create_entry(title="", data=user_input)
