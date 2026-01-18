"""Constants for Mercury Switch integration."""

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "mercury_switch"

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]

DEFAULT_NAME = "Mercury Switch"
SCAN_INTERVAL = timedelta(seconds=30)
DEFAULT_CONF_TIMEOUT = timedelta(seconds=15)
KEY_COORDINATOR_SWITCH_INFOS = "coordinator_switch_infos"
KEY_SWITCH = "switch"
ON_VALUES = ["on", True]
OFF_VALUES = ["off", False]
