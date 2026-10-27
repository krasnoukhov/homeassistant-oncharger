"""Constants for the Oncharger integration."""

from enum import StrEnum
from homeassistant.const import CONF_IP_ADDRESS

DOMAIN = "oncharger"
HTTP_TIMEOUT = 5
CLOUD_UPDATE_INTERVAL = 30
LOCAL_UPDATE_INTERVAL = 5
URL_BASE = "https://my.oncharger.com"

ATTR_ENTITY = "entity"

CLOUD = "cloud"
CONNECTION_TYPE = "connection_type"
DC_CHARGER = "dc_charger"
DEVICE_NAME = "device_name"
DEVICE_TYPE = "device_type"
IP_ADDRESS = CONF_IP_ADDRESS
LOCAL = "local"
PASSWORD = "password"
PHASE_CURRENT_ENTITY = "phase_current_entity"
PHASE_MAX_LOAD_MIN = 10
PHASE_MAX_LOAD = "phase_max_load"
SINGLE_PHASE = "single_phase"
THREE_PHASE = "three_phase"
USERNAME = "username"

CHARGER_CCS_SLOT_KEY = "wtbConnId"
CHARGER_CURRENT_VERSION_KEY = "ver"
CHARGER_GBT_SLOT_KEY = "gbtConnId"
CHARGER_LOCKED_UNLOCKED_2_KEY = "loc2"
CHARGER_LOCKED_UNLOCKED_KEY = "loc"
CHARGER_MAX_AVAILABLE_POWER_KEY = "mp"
CHARGER_MAX_CHARGING_CURRENT_KEY = "pilot"
CHARGER_MAX_POWER_KEY = "power_max"
CHARGER_NAME_KEY = "ocid"
CHARGER_POWER_LIMIT_KEY = "power_set"
CHARGER_SOC_LIMIT_KEY = "soc_set"

CHARGER_BOOST_TYPE_KEY = "chargeBoostType"
CHARGER_BOOST_NATIVE_KEY = "remotePMCon"
CHARGER_CURRENT_KEY = "amp"
CHARGER_DEVICE_TEMPERATURE_KEY = "temp1"
CHARGER_OUTPUT_CURRENT_KEY = "current_now"
CHARGER_OUTPUT_POWER_KEY = "power_now"
CHARGER_OUTPUT_VOLTAGE_KEY = "volt_now"
CHARGER_PROTOCOL_KEY = "protocol_type"
CHARGER_REQUESTED_CURRENT_KEY = "current_target"
CHARGER_SESSION_ELAPSED_KEY = "elapsed"
CHARGER_SESSION_ENERGY_KEY = "wsec"
CHARGER_SOC_KEY = "soc_now"
CHARGER_STATE_KEY = "state"
CHARGER_TARGET_VOLTAGE_KEY = "volt_target"
CHARGER_TOTAL_ENERGY_KEY = "wat"
CHARGER_V2G_MODE_KEY = "v2g_mode"
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

CHARGER_PROTOCOL: dict[int, str] = {0: "none", 1: "gbt", 2: "ccs"}

CHARGER_V2G_MODE: dict[int, str] = {0: "charger", 1: "on_grid", 2: "off_grid"}
