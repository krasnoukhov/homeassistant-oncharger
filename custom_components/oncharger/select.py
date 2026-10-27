"""Home Assistant component for accessing the Oncharger API.

The select component creates a select entity."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CHARGER_V2G_MODE, CHARGER_V2G_MODE_KEY, DOMAIN, IP_ADDRESS
from .coordinator import OnchargerCoordinator
from .entity import OnchargerEntity

# Off-grid: the charger does not limit power, it gives up to its rating
# until its overload protection switches it off
V2G_MODE_DESCRIPTION = SelectEntityDescription(
    key=CHARGER_V2G_MODE_KEY,
    translation_key="v2g_mode",
    icon="mdi:transmission-tower-export",
    options=list(CHARGER_V2G_MODE.values()),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create Oncharger select entities in HASS."""
    coordinator: OnchargerCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Bidirectional DC chargers, local only
    if entry.data.get(IP_ADDRESS) and CHARGER_V2G_MODE_KEY in coordinator.data:
        async_add_entities(
            [OnchargerV2GModeSelect(hass, coordinator, entry, V2G_MODE_DESCRIPTION)]
        )


class OnchargerV2GModeSelect(OnchargerEntity, SelectEntity):
    """Representation of the Oncharger V2G operating mode."""

    @property
    def current_option(self) -> str | None:
        """Return the selected mode."""
        return CHARGER_V2G_MODE.get(self.coordinator.data[CHARGER_V2G_MODE_KEY])

    async def async_select_option(self, option: str) -> None:
        """Change the mode, the charger restarts its power module."""
        mode = next(k for k, v in CHARGER_V2G_MODE.items() if v == option)
        await self.coordinator.async_set_param(CHARGER_V2G_MODE_KEY, mode)
