"""The Oncharger integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.const import Platform

from .oncharger import Oncharger
from .coordinator import InvalidAuth, OnchargerCoordinator
from .const import DOMAIN

PLATFORMS = [Platform.SENSOR, Platform.NUMBER, Platform.LOCK, Platform.SWITCH]

_LOGGER = logging.getLogger(__name__)


async def update_listener(hass, entry):
    """Handle options update."""
    coordinator: OnchargerCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_request_refresh()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Oncharger from a config entry."""
    _LOGGER.debug(f"Oncharger entry data: {entry.data}")
    _LOGGER.debug(f"Oncharger entry options: {entry.options}")

    oncharger = Oncharger(entry.data)
    coordinator = OnchargerCoordinator(
        oncharger,
        hass,
    )

    try:
        await coordinator.async_validate_input()

    except InvalidAuth as invalid_auth_error:
        raise ConfigEntryAuthFailed from invalid_auth_error

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
