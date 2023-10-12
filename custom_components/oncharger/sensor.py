"""Home Assistant component for accessing the Oncharger API.

The sensor component creates multipe sensors regarding Oncharger status.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import cast, Callable, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfTemperature,
    UnitOfEnergy,
    UnitOfTime,
    UnitOfElectricPotential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    CHARGER_CURRENT_KEY,
    CHARGER_DEVICE_TEMPERATURE_KEY,
    CHARGER_SESSION_ELAPSED_KEY,
    CHARGER_SESSION_ENERGY_KEY,
    CHARGER_STATE_KEY,
    CHARGER_STATE,
    CHARGER_TOTAL_ENERGY_KEY,
    CHARGER_VOLTAGE_KEY,
    ChargerState,
    DOMAIN,
)
from .coordinator import OnchargerCoordinator
from .entity import OnchargerEntity


@dataclass
class OnchargerSensorEntityDescription(SensorEntityDescription):
    """Describes Oncharger sensor entity."""

    normalize: Callable[[Any], Any] | None = None


ENTITY_DESCRIPTIONS: dict[str, OnchargerSensorEntityDescription] = {
    CHARGER_STATE_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_STATE_KEY,
        translation_key="state",
        icon="mdi:ev-station",
        normalize=lambda value: CHARGER_STATE.get(value, ChargerState.ERROR),
    ),
    CHARGER_CURRENT_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_CURRENT_KEY,
        translation_key="current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        normalize=lambda value: value / 1000,
    ),
    CHARGER_SESSION_ENERGY_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_SESSION_ENERGY_KEY,
        translation_key="session_energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        normalize=lambda value: value / (36 * 100000),
    ),
    CHARGER_DEVICE_TEMPERATURE_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_DEVICE_TEMPERATURE_KEY,
        translation_key="device_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=2,
        normalize=lambda value: value / 10,
    ),
    CHARGER_SESSION_ELAPSED_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_SESSION_ELAPSED_KEY,
        translation_key="session_elapsed",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        normalize=lambda value: value,
    ),
    CHARGER_VOLTAGE_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_VOLTAGE_KEY,
        translation_key="voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=2,
        normalize=lambda value: value / 10,
    ),
    CHARGER_TOTAL_ENERGY_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_TOTAL_ENERGY_KEY,
        translation_key="total_energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        normalize=lambda value: value / 1000,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create Oncharger sensor entities in HASS."""
    coordinator: OnchargerCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            OnchargerSensor(hass, coordinator, entry, description)
            for ent in coordinator.data
            if (description := ENTITY_DESCRIPTIONS.get(ent))
        ]
    )


class OnchargerSensor(OnchargerEntity, SensorEntity):
    """Representation of the Oncharger sensor."""

    entity_description: OnchargerSensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = self.coordinator.data[self.entity_description.key]
        return cast(StateType, self.entity_description.normalize(value))
