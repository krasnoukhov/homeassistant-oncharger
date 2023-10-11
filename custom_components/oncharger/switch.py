"""Home Assistant component for accessing the Oncharger API.

The switch component creates a switch entity."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CHARGER_BOOST_NATIVE_KEY,
    CHARGER_BOOST_TYPE_KEY,
    DOMAIN,
    PHASE_CURRENT_ENTITY,
    PHASE_MAX_LOAD,
)
from .coordinator import OnchargerCoordinator
from .entity import OnchargerEntity

ENTITY_DESCRIPTIONS: dict[str, SwitchEntityDescription] = {
    CHARGER_BOOST_TYPE_KEY: SwitchEntityDescription(
        key=CHARGER_BOOST_TYPE_KEY, translation_key="boost", icon="mdi:auto-mode"
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create Oncharger switch entities in HASS."""
    coordinator: OnchargerCoordinator = hass.data[DOMAIN][entry.entry_id]

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
    def available(self) -> bool:
        """Return the availability of the switch."""
        """If user didn't set the entity, we are not available."""
        """If user has native device boosting, we don't want to interfere."""
        return (
            super().available
            and self._entry.options.get(PHASE_CURRENT_ENTITY)
            and self.coordinator.data[CHARGER_BOOST_NATIVE_KEY] == 0
        )

    @property
    def is_on(self) -> bool:
        """Return the status of the switch."""
        # TODO: logic for the switch
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
