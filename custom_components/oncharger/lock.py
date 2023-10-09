"""Home Assistant component for accessing the Oncharger API.

The lock component creates a lock entity."""
from __future__ import annotations

from homeassistant.components.lock import LockEntity, LockEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CHARGER_LOCKED_UNLOCKED_KEY,
    DOMAIN,
)
from .coordinator import OnchargerCoordinator
from .entity import OnchargerEntity

ENTITY_DESCRIPTIONS: dict[str, LockEntityDescription] = {
    CHARGER_LOCKED_UNLOCKED_KEY: LockEntityDescription(
        key=CHARGER_LOCKED_UNLOCKED_KEY,
        translation_key="lock",
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create Oncharger lock entities in HASS."""
    coordinator: OnchargerCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            OnchargerLock(coordinator, entry, description)
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
