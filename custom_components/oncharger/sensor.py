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
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    CHARGER_CURRENT_KEY,
    CHARGER_CURRENT1_KEY,
    CHARGER_CURRENT2_KEY,
    CHARGER_CURRENT3_KEY,
    CHARGER_DEVICE_TEMPERATURE_KEY,
    CHARGER_SESSION_ELAPSED_KEY,
    CHARGER_SESSION_ENERGY_KEY,
    CHARGER_STATE_KEY,
    CHARGER_STATE,
    CHARGER_TOTAL_ENERGY_KEY,
    CHARGER_VOLTAGE_KEY,
    CHARGER_VOLTAGE1_KEY,
    CHARGER_VOLTAGE2_KEY,
    CHARGER_VOLTAGE3_KEY,
    ChargerState,
    DEVICE_TYPE,
    DOMAIN,
    SINGLE_PHASE,
    THREE_PHASE,
)
from .coordinator import OnchargerCoordinator
from .entity import OnchargerEntity


@dataclass
class OnchargerSensorEntityDescription(SensorEntityDescription):
    """Describes Oncharger sensor entity."""

    normalize: Callable[[Any], Any] | None = None


POWER_KEY = "power"
POWER1_KEY = "power1"
POWER2_KEY = "power2"
POWER3_KEY = "power3"
TOTAL_POWER_KEY = "total_power"

SESSION_ENERGY_DESCRIPTION = OnchargerSensorEntityDescription(
    key=CHARGER_SESSION_ENERGY_KEY,
    translation_key="session_energy",
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL,
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    suggested_display_precision=2,
    normalize=lambda value: round(value / (36 * 100000), 2),
)

TOTAL_ENERGY_DESCRIPTION = OnchargerSensorEntityDescription(
    key=CHARGER_TOTAL_ENERGY_KEY,
    translation_key="total_energy",
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    suggested_display_precision=2,
    normalize=lambda value: round(value / 1000, 2),
)

POWER_DESCRIPTION = OnchargerSensorEntityDescription(
    key=POWER_KEY,
    translation_key=POWER_KEY,
    icon="mdi:ev-plug-type2",
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfPower.WATT,
    suggested_display_precision=0,
)

POWER1_DESCRIPTION = OnchargerSensorEntityDescription(
    key=POWER1_KEY,
    translation_key=POWER1_KEY,
    icon="mdi:ev-plug-type2",
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfPower.WATT,
    suggested_display_precision=0,
)

POWER2_DESCRIPTION = OnchargerSensorEntityDescription(
    key=POWER2_KEY,
    translation_key=POWER2_KEY,
    icon="mdi:ev-plug-type2",
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfPower.WATT,
    suggested_display_precision=0,
)

POWER3_DESCRIPTION = OnchargerSensorEntityDescription(
    key=POWER3_KEY,
    translation_key=POWER3_KEY,
    icon="mdi:ev-plug-type2",
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfPower.WATT,
    suggested_display_precision=0,
)

TOTAL_POWER_DESCRIPTION = OnchargerSensorEntityDescription(
    key=TOTAL_POWER_KEY,
    translation_key=TOTAL_POWER_KEY,
    icon="mdi:ev-plug-type2",
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfPower.WATT,
    suggested_display_precision=0,
)

ENTITY_DESCRIPTIONS: dict[str, OnchargerSensorEntityDescription] = {
    CHARGER_STATE_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_STATE_KEY,
        translation_key="state",
        icon="mdi:ev-station",
        normalize=lambda value: CHARGER_STATE.get(value, ChargerState.ERROR),
    ),
    CHARGER_SESSION_ENERGY_KEY: SESSION_ENERGY_DESCRIPTION,
    CHARGER_DEVICE_TEMPERATURE_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_DEVICE_TEMPERATURE_KEY,
        translation_key="device_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=2,
        normalize=lambda value: round(value / 10, 2),
    ),
    CHARGER_SESSION_ELAPSED_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_SESSION_ELAPSED_KEY,
        translation_key="session_elapsed",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        normalize=lambda value: value,
    ),
}

ENTITY_DESCRIPTIONS_1P: dict[str, OnchargerSensorEntityDescription] = {
    CHARGER_CURRENT_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_CURRENT_KEY,
        translation_key="current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        normalize=lambda value: round(value / 1000, 2),
    ),
    CHARGER_VOLTAGE_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_VOLTAGE_KEY,
        translation_key="voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=2,
        normalize=lambda value: round(value / 10, 2),
    ),
}

ENTITY_DESCRIPTIONS_3P: dict[str, OnchargerSensorEntityDescription] = {
    CHARGER_CURRENT1_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_CURRENT1_KEY,
        translation_key="current1",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        normalize=lambda value: round(value / 1000, 2),
    ),
    CHARGER_CURRENT2_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_CURRENT2_KEY,
        translation_key="current2",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        normalize=lambda value: round(value / 1000, 2),
    ),
    CHARGER_CURRENT3_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_CURRENT3_KEY,
        translation_key="current3",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        normalize=lambda value: round(value / 1000, 2),
    ),
    CHARGER_VOLTAGE1_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_VOLTAGE1_KEY,
        translation_key="voltage1",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=2,
        normalize=lambda value: round(value / 10, 2),
    ),
    CHARGER_VOLTAGE2_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_VOLTAGE2_KEY,
        translation_key="voltage2",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=2,
        normalize=lambda value: round(value / 10, 2),
    ),
    CHARGER_VOLTAGE3_KEY: OnchargerSensorEntityDescription(
        key=CHARGER_VOLTAGE3_KEY,
        translation_key="voltage3",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=2,
        normalize=lambda value: round(value / 10, 2),
    ),
}

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create Oncharger sensor entities in HASS."""
    coordinator: OnchargerCoordinator = hass.data[DOMAIN][entry.entry_id]
    dev_type = entry.data[DEVICE_TYPE]

    async_add_entities(
        [
            OnchargerSensor(hass, coordinator, entry, description)
            for ent in coordinator.data
            if (description := ENTITY_DESCRIPTIONS.get(ent))
        ]
    )
    if dev_type == SINGLE_PHASE:
        async_add_entities(
            [
                OnchargerSensor(hass, coordinator, entry, description)
                for ent in coordinator.data
                if (description := ENTITY_DESCRIPTIONS_1P.get(ent))
            ]
        )
    if dev_type == THREE_PHASE:
        async_add_entities(
            [
                OnchargerSensor(hass, coordinator, entry, description)
                for ent in coordinator.data
                if (description := ENTITY_DESCRIPTIONS_3P.get(ent))
            ]
        )
    async_add_entities(
        [OnchargerTotalEnergySensor(hass, coordinator, entry, TOTAL_ENERGY_DESCRIPTION)]
    )
    if dev_type == SINGLE_PHASE:
        async_add_entities(
            [OnchargerPowerSensor(hass, coordinator, entry, POWER_DESCRIPTION)]
        )
    if dev_type == THREE_PHASE:
        async_add_entities(
            [OnchargerPower1Sensor(hass, coordinator, entry, POWER1_DESCRIPTION)]
        )
        async_add_entities(
            [OnchargerPower2Sensor(hass, coordinator, entry, POWER2_DESCRIPTION)]
        )
        async_add_entities(
            [OnchargerPower3Sensor(hass, coordinator, entry, POWER3_DESCRIPTION)]
        )
        async_add_entities(
            [OnchargerTotalPowerSensor(hass, coordinator, entry, TOTAL_POWER_DESCRIPTION)]
        )


class OnchargerSensor(OnchargerEntity, SensorEntity):
    """Representation of the Oncharger sensor."""

    entity_description: OnchargerSensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = self.coordinator.data[self.entity_description.key]
        return cast(StateType, self.entity_description.normalize(value))


class OnchargerTotalEnergySensor(OnchargerSensor):
    """Representation of the Oncharger total energy sensor."""

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = self.entity_description.normalize(
            self.coordinator.data[self.entity_description.key]
        )
        session_energy = SESSION_ENERGY_DESCRIPTION.normalize(
            self.coordinator.data[SESSION_ENERGY_DESCRIPTION.key]
        )
        return cast(StateType, value) + cast(StateType, session_energy)


class OnchargerPowerSensor(OnchargerSensor):
    """Representation of the Oncharger power sensor."""

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = (
            self.coordinator.data[CHARGER_CURRENT_KEY]
            * self.coordinator.data[CHARGER_VOLTAGE_KEY]
        ) / 10000
        return cast(StateType, value)

class OnchargerPower1Sensor(OnchargerSensor):
    """Representation of the Oncharger power1 sensor."""

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = (
            self.coordinator.data[CHARGER_CURRENT1_KEY]
            * self.coordinator.data[CHARGER_VOLTAGE1_KEY]
        ) / 10000
        return cast(StateType, value)

class OnchargerPower2Sensor(OnchargerSensor):
    """Representation of the Oncharger power2 sensor."""

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = (
            self.coordinator.data[CHARGER_CURRENT2_KEY]
            * self.coordinator.data[CHARGER_VOLTAGE2_KEY]
        ) / 10000
        return cast(StateType, value)

class OnchargerPower3Sensor(OnchargerSensor):
    """Representation of the Oncharger power3 sensor."""

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = round((
            self.coordinator.data[CHARGER_CURRENT3_KEY]
            * self.coordinator.data[CHARGER_VOLTAGE3_KEY]
        ) / 10000, 0)
        return cast(StateType, value)

class OnchargerTotalPowerSensor(OnchargerSensor):
    """Representation of the Oncharger total power sensor."""

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = round((
            self.coordinator.data[CHARGER_CURRENT1_KEY]
            * self.coordinator.data[CHARGER_VOLTAGE1_KEY] +
            self.coordinator.data[CHARGER_CURRENT2_KEY]
            * self.coordinator.data[CHARGER_VOLTAGE2_KEY] +
            self.coordinator.data[CHARGER_CURRENT3_KEY]
            * self.coordinator.data[CHARGER_VOLTAGE3_KEY]
        ) / 10000, 0)
        return cast(StateType, value)
