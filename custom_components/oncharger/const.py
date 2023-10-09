"""Constants for the Oncharger integration."""
from enum import StrEnum
from homeassistant.const import CONF_IP_ADDRESS

DOMAIN = "oncharger"
HTTP_TIMEOUT = 5
UPDATE_INTERVAL = 30

CLOUD = "cloud"
CONNECTION_TYPE = "connection_type"
DEVICE_NAME = "device_name"
IP_ADDRESS = CONF_IP_ADDRESS
LOCAL = "local"
PASSWORD = "password"
USERNAME = "username"

CHARGER_CURRENT_VERSION_KEY = "ver"
CHARGER_LOCKED_UNLOCKED_KEY = "loc"
CHARGER_MAX_AVAILABLE_POWER_KEY = "mp"
CHARGER_MAX_CHARGING_CURRENT_KEY = "pilot"
CHARGER_NAME_KEY = "ocid"

CHARGER_CURRENT_KEY = "amp"
CHARGER_DEVICE_TEMPERATURE_KEY = "temp1"
CHARGER_SESSION_ELAPSED_KEY = "elapsed"
CHARGER_SESSION_ENERGY_KEY = "wsec"
CHARGER_STATE_KEY = "state"
CHARGER_TOTAL_ENERGY_KEY = "wat"
CHARGER_VOLTAGE_KEY = "volt"


class ChargerState(StrEnum):
    """Charger Status Description."""

    READY = "Ready"
    CONNECTED = "Connected"
    CHARGING = "Charging"
    ERROR = "Error"


CHARGER_STATE: dict[int, ChargerState] = {
    1: ChargerState.READY,
    2: ChargerState.CONNECTED,
    3: ChargerState.CHARGING,
}
