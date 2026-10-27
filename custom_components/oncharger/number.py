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
from homeassistant.const import UnitOfElectricCurrent, UnitOfPower, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CHARGER_MAX_AVAILABLE_POWER_KEY,
    CHARGER_MAX_CHARGING_CURRENT_KEY,
    CHARGER_MAX_POWER_KEY,
    CHARGER_POWER_LIMIT_KEY,
    CHARGER_SOC_LIMIT_KEY,
    DC_CHARGER,
    DEVICE_TYPE,
    DOMAIN,
    IP_ADDRESS,
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

POWER_LIMIT_DESCRIPTION = NumberEntityDescription(
    key=CHARGER_POWER_LIMIT_KEY,
    translation_key="power_limit",
    device_class=NumberDeviceClass.POWER,
    native_unit_of_measurement=UnitOfPower.WATT,
    native_min_value=1000,
    native_step=100,
    mode=NumberMode.BOX,
)

SOC_LIMIT_DESCRIPTION = NumberEntityDescription(
    key=CHARGER_SOC_LIMIT_KEY,
    translation_key="charge_limit",
    device_class=NumberDeviceClass.BATTERY,
    native_unit_of_measurement=PERCENTAGE,
    native_min_value=20,
    native_max_value=100,
    mode=NumberMode.BOX,
)


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

    # Support DC settings for local only
    if entry.data.get(IP_ADDRESS) and entry.data.get(DEVICE_TYPE) == DC_CHARGER:
        async_add_entities(
            [
                OnchargerPowerLimit(hass, coordinator, entry, POWER_LIMIT_DESCRIPTION),
                OnchargerChargeLimit(hass, coordinator, entry, SOC_LIMIT_DESCRIPTION),
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


class OnchargerPowerLimit(OnchargerEntity, NumberEntity):
    """Representation of the Oncharger DC power limit."""

    @property
    def native_max_value(self) -> float:
        """Return the charger rated power."""
        return cast(float, self.coordinator.data[CHARGER_MAX_POWER_KEY] * 1000)

    @property
    def native_value(self) -> float | None:
        """Return the value of the entity."""
        return cast(float | None, self.coordinator.data[CHARGER_POWER_LIMIT_KEY])

    async def async_set_native_value(self, value: float) -> None:
        """Set the value of the entity."""
        await self.coordinator.async_set_param("power_set_watt", int(value))


class OnchargerChargeLimit(OnchargerEntity, NumberEntity):
    """Representation of the Oncharger DC charge limit."""

    @property
    def native_value(self) -> float | None:
        """Return the value of the entity."""
        return cast(float | None, self.coordinator.data[CHARGER_SOC_LIMIT_KEY])

    async def async_set_native_value(self, value: float) -> None:
        """Set the value of the entity."""
        await self.coordinator.async_set_param(CHARGER_SOC_LIMIT_KEY, int(value))
