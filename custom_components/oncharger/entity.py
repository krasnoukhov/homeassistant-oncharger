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
    IP_ADDRESS,
    URL_BASE,
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

        self.hass = hass
        self.entity_description = description
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
        configuration_url = (
            f"http://{self._entry.data[IP_ADDRESS]}"
            if self._entry.data.get(IP_ADDRESS)
            else f"{URL_BASE}/{self.coordinator.data[CHARGER_NAME_KEY]}"
        )

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
            configuration_url=configuration_url,
        )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        original = super().name
        key = self.entity_description.key
        suffix = f" {key[-1]}" if key[-1] in ["1", "2", "3"] else ""
        return f"{original}{suffix}"
