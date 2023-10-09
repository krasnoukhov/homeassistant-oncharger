"""The Oncharger integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.const import Platform

from .oncharger import Oncharger
from .coordinator import InvalidAuth, OnchargerCoordinator
from .const import DOMAIN

PLATFORMS = [Platform.SENSOR, Platform.NUMBER, Platform.LOCK]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Oncharger from a config entry."""
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

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
