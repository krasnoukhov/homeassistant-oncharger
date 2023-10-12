"""Base entity for the Oncharger integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CHARGER_CURRENT_VERSION_KEY,
    CHARGER_NAME_KEY,
    DEVICE_NAME,
    DOMAIN,
)
from .coordinator import OnchargerCoordinator


class OnchargerEntity(CoordinatorEntity[OnchargerCoordinator]):
    """Defines a base Oncharger entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: OnchargerCoordinator,
        entry: ConfigEntry,
        description: EntityDescription,
    ) -> None:
        """Initialize a Oncharger entity."""
        super().__init__(coordinator)
        self.entity_description = description

        self._hass = hass
        self._coordinator = coordinator
        self._entry = entry

        self._attr_unique_id = "-".join(
            [
                coordinator.data[CHARGER_NAME_KEY],
                entry.data[DEVICE_NAME],
                description.key,
            ]
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Oncharger device."""
        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    self.coordinator.data[CHARGER_NAME_KEY],
                    self._entry.data[DEVICE_NAME],
                )
            },
            name=self._entry.data[DEVICE_NAME],
            manufacturer="Oncharger",
            model="Wi-Fi",
            sw_version=self.coordinator.data[CHARGER_CURRENT_VERSION_KEY],
        )
