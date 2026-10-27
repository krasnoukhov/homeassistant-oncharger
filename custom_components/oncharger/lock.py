"""Home Assistant component for accessing the Oncharger API.

The lock component creates a lock entity."""

from __future__ import annotations

from homeassistant.components.lock import LockEntity, LockEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CHARGER_CCS_SLOT_KEY,
    CHARGER_GBT_SLOT_KEY,
    CHARGER_LOCKED_UNLOCKED_2_KEY,
    CHARGER_LOCKED_UNLOCKED_KEY,
    DOMAIN,
    IP_ADDRESS,
)
from .coordinator import OnchargerCoordinator
from .entity import OnchargerEntity

ENTITY_DESCRIPTIONS: dict[str, LockEntityDescription] = {
    CHARGER_LOCKED_UNLOCKED_KEY: LockEntityDescription(
        key=CHARGER_LOCKED_UNLOCKED_KEY,
        translation_key="lock",
    ),
}

LOCKED_KEYS = {1: CHARGER_LOCKED_UNLOCKED_KEY, 2: CHARGER_LOCKED_UNLOCKED_2_KEY}

CONNECTOR_DESCRIPTIONS: list[LockEntityDescription] = [
    LockEntityDescription(key=CHARGER_CCS_SLOT_KEY, translation_key="ccs_lock"),
    LockEntityDescription(key=CHARGER_GBT_SLOT_KEY, translation_key="gbt_lock"),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create Oncharger lock entities in HASS."""
    coordinator: OnchargerCoordinator = hass.data[DOMAIN][entry.entry_id]

    # CCS and GBT connectors on separate slots, each with its own lock
    ccs_slot = coordinator.data.get(CHARGER_CCS_SLOT_KEY)
    gbt_slot = coordinator.data.get(CHARGER_GBT_SLOT_KEY)
    if entry.data.get(IP_ADDRESS) and ccs_slot and gbt_slot and ccs_slot != gbt_slot:
        async_add_entities(
            [
                OnchargerConnectorLock(hass, coordinator, entry, description)
                for description in CONNECTOR_DESCRIPTIONS
            ]
        )
        return

    async_add_entities(
        [
            OnchargerLock(hass, coordinator, entry, description)
            for ent in coordinator.data
            if (description := ENTITY_DESCRIPTIONS.get(ent))
        ]
    )


class OnchargerLock(OnchargerEntity, LockEntity):
    """Representation of a Oncharger lock."""

    @property
    def is_locked(self) -> bool:
        """Return the status of the lock."""
        return self.coordinator.data[CHARGER_LOCKED_UNLOCKED_KEY]  # type: ignore[no-any-return]

    async def async_lock(self) -> None:
        """Lock charger."""
        await self.coordinator.async_set_lock_unlock(True)

    async def async_unlock(self) -> None:
        """Unlock charger."""
        await self.coordinator.async_set_lock_unlock(False)


class OnchargerConnectorLock(OnchargerEntity, LockEntity):
    """Representation of a Oncharger connector lock."""

    @property
    def slot(self) -> int:
        """Return the slot of the connector."""
        return self.coordinator.data[self.entity_description.key]

    @property
    def is_locked(self) -> bool:
        """Return the status of the lock."""
        return bool(self.coordinator.data[LOCKED_KEYS[self.slot]])

    async def async_lock(self) -> None:
        """Lock connector."""
        await self.coordinator.async_set_lock_unlock(True, self.slot)

    async def async_unlock(self) -> None:
        """Unlock connector, the charger locks the other one."""
        await self.coordinator.async_set_lock_unlock(False, self.slot)
