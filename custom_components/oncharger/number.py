"""Home Assistant component for accessing the Oncharger API.

The number component allows control of charging current.
"""
from __future__ import annotations

from typing import cast

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
    NumberDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CHARGER_MAX_AVAILABLE_POWER_KEY,
    CHARGER_MAX_CHARGING_CURRENT_KEY,
    DOMAIN,
)
from .coordinator import OnchargerCoordinator
from .entity import OnchargerEntity


ENTITY_DESCRIPTIONS: dict[str, NumberEntityDescription] = {
    CHARGER_MAX_CHARGING_CURRENT_KEY: NumberEntityDescription(
        key=CHARGER_MAX_CHARGING_CURRENT_KEY,
        translation_key="maximum_charging_current",
        device_class=NumberDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        native_min_value=6,
        mode=NumberMode.BOX,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create Oncharger number entities in HASS."""
    coordinator: OnchargerCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            OnchargerNumber(hass, coordinator, entry, description)
            for ent in coordinator.data
            if (description := ENTITY_DESCRIPTIONS.get(ent))
        ]
    )


class OnchargerNumber(OnchargerEntity, NumberEntity):
    """Representation of the Oncharger number."""

    entity_description: NumberEntityDescription

    @property
    def native_max_value(self) -> float:
        """Return the maximum available current."""
        return cast(float, self.coordinator.data[CHARGER_MAX_AVAILABLE_POWER_KEY])

    @property
    def native_value(self) -> float | None:
        """Return the value of the entity."""
        return cast(
            float | None, self.coordinator.data[CHARGER_MAX_CHARGING_CURRENT_KEY]
        )

    async def async_set_native_value(self, value: float) -> None:
        """Set the value of the entity."""
        await self.coordinator.async_set_charging_current(value)
