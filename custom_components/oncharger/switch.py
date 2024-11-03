"""Home Assistant component for accessing the Oncharger API.

The switch component creates a switch entity."""

from __future__ import annotations
import logging
import math

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    STATE_UNKNOWN,
    ATTR_UNIT_OF_MEASUREMENT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change
from homeassistant.util.unit_conversion import ElectricCurrentConverter

from .const import (
    CHARGER_BOOST_NATIVE_KEY,
    CHARGER_BOOST_TYPE_KEY,
    CHARGER_MAX_CHARGING_CURRENT_KEY,
    DOMAIN,
    IP_ADDRESS,
    PHASE_CURRENT_ENTITY,
    PHASE_MAX_LOAD_MIN,
    PHASE_MAX_LOAD,
)
from .coordinator import OnchargerCoordinator
from .entity import OnchargerEntity

ENTITY_DESCRIPTIONS: dict[str, SwitchEntityDescription] = {
    CHARGER_BOOST_TYPE_KEY: SwitchEntityDescription(
        key=CHARGER_BOOST_TYPE_KEY, translation_key="boost", icon="mdi:auto-mode"
    ),
}

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create Oncharger switch entities in HASS."""
    coordinator: OnchargerCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Support boost for local only
    if entry.data.get(IP_ADDRESS):
        async_add_entities(
            [
                OnchargerSwitch(hass, coordinator, entry, description)
                for ent in coordinator.data
                if (description := ENTITY_DESCRIPTIONS.get(ent))
            ]
        )


class OnchargerSwitch(OnchargerEntity, SwitchEntity):
    """Representation of a Oncharger switch."""

    @property
    def phase_current_entity_id(self) -> str | None:
        """Return the entity id for phase current."""
        return self._entry.options.get(PHASE_CURRENT_ENTITY)

    @property
    def available(self) -> bool:
        """Return the availability of the switch.
        If user didn't set the entity, we are not available.
        If user has native device boosting, we don't want to interfere."""
        return (
            super().available
            and self.phase_current_entity_id
            and self.coordinator.data[CHARGER_BOOST_NATIVE_KEY] == 0
        )

    @property
    def is_on(self) -> bool:
        """Return the status of the switch."""
        return self.coordinator.data[CHARGER_BOOST_TYPE_KEY] == 5

    async def async_turn_on(self) -> None:
        """Switch boost."""
        await self.coordinator.async_set_boost_config(
            5,
            self._entry.options[PHASE_MAX_LOAD],
            0,
            "",
        )

    async def async_turn_off(self) -> None:
        """Unswitch boost."""
        await self.coordinator.async_set_boost_config(
            0,
            self._entry.options[PHASE_MAX_LOAD],
            0,
            "",
        )
        await self._async_set_charging_current(PHASE_MAX_LOAD_MIN)

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        async def update_listener(_hass, _entry):
            if self.available and self.is_on:
                await self._async_trigger_phase_current_changed()

        self._entry.async_on_unload(self._entry.add_update_listener(update_listener))
        await update_listener(self.hass, self._entry)

        if not self.phase_current_entity_id:
            return

        async_track_state_change(
            self.hass,
            self.phase_current_entity_id,
            self._async_phase_current_changed,
        )

    async def _async_trigger_phase_current_changed(self):
        await self._async_phase_current_changed(
            self.phase_current_entity_id,
            None,
            self.hass.states.get(self.phase_current_entity_id),
        )

    async def _async_phase_current_changed(self, _entity_id, _old_state, new_state):
        """Handle phase current changes."""

        if not self.available or not self.is_on:
            return

        if (
            new_state is None
            or new_state.state is None
            or new_state.state == STATE_UNKNOWN
        ):
            return await self._async_set_charging_current(PHASE_MAX_LOAD_MIN)

        try:
            current = float(new_state.state)
        except Exception as exception_error:  # pylint: disable=broad-except
            _LOGGER.exception(
                f"Unexpected exception in phase current {exception_error}"
            )
            return await self._async_set_charging_current(PHASE_MAX_LOAD_MIN)

        unit_of_measurement = new_state.attributes[ATTR_UNIT_OF_MEASUREMENT]
        if unit_of_measurement:
            current = ElectricCurrentConverter.convert(
                current, unit_of_measurement, UnitOfElectricCurrent.AMPERE
            )

        available_current = self._entry.options[PHASE_MAX_LOAD] - math.ceil(current)
        if available_current != float(
            self.coordinator.data[CHARGER_MAX_CHARGING_CURRENT_KEY]
        ):
            await self._async_set_charging_current(available_current)

    async def _async_set_charging_current(self, value: float) -> None:
        """Set the charging current."""
        _LOGGER.debug(f"Oncharger boost setting current: {value}")
        await self.coordinator.async_set_charging_current(value)
