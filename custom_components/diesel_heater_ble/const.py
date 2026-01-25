"""Constants for Diesel Heater BLE integration."""
from enum import IntEnum

DOMAIN = "diesel_heater_ble"

# BLE UUIDs
SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
WRITE_CHARACTERISTIC_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"
NOTIFY_CHARACTERISTIC_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"

# Command header
CMD_HEADER = bytes([0xBA, 0xAB])
CMD_LENGTH = 0x04

# Command types
CMD_TYPE_STATUS = 0xCC
CMD_TYPE_CONTROL = 0xBB

# Control command codes
CMD_POWER_TOGGLE = 0xA1
CMD_UP = 0xA2
CMD_DOWN = 0xA3
CMD_FAN_MODE = 0xA4
CMD_CELSIUS = 0xA7
CMD_FAHRENHEIT = 0xA8
CMD_LEVEL_MODE = 0xAC
CMD_TEMP_MODE = 0xAD

# Pre-built commands (8 bytes each)
CMD_GET_STATUS = bytes([0xBA, 0xAB, 0x04, 0xCC, 0x00, 0x00, 0x00, 0x35])
CMD_TOGGLE_POWER = bytes([0xBA, 0xAB, 0x04, 0xBB, 0xA1, 0x00, 0x00, 0xC5])
CMD_PRESS_UP = bytes([0xBA, 0xAB, 0x04, 0xBB, 0xA2, 0x00, 0x00, 0xC6])
CMD_PRESS_DOWN = bytes([0xBA, 0xAB, 0x04, 0xBB, 0xA3, 0x00, 0x00, 0xC7])
CMD_SET_FAN_MODE = bytes([0xBA, 0xAB, 0x04, 0xBB, 0xA4, 0x00, 0x00, 0xC8])
CMD_SET_CELSIUS = bytes([0xBA, 0xAB, 0x04, 0xBB, 0xA7, 0x00, 0x00, 0xCB])
CMD_SET_FAHRENHEIT = bytes([0xBA, 0xAB, 0x04, 0xBB, 0xA8, 0x00, 0x00, 0xCC])
CMD_SET_LEVEL_MODE = bytes([0xBA, 0xAB, 0x04, 0xBB, 0xAC, 0x00, 0x00, 0xD0])
CMD_SET_TEMP_MODE = bytes([0xBA, 0xAB, 0x04, 0xBB, 0xAD, 0x00, 0x00, 0xD1])

# Response header
RESPONSE_HEADER = bytes([0xAB, 0xBA, 0x11, 0xCC])
RESPONSE_LENGTH = 21


class OperatingMode(IntEnum):
    """Heater operating mode."""

    IDLE = 0
    HEATING = 1
    COOLING = 2
    FAN_ONLY = 4


class ControlMode(IntEnum):
    """Heater control mode."""

    LEVEL = 0
    TEMPERATURE = 1
    ERROR = 0xFF


class RunningState(IntEnum):
    """Heater running state."""

    IDLE = 0
    COOLING = 1
    GLOWPLUG = 3
    HEATING = 5
    PREHEATING = 7


class TemperatureUnit(IntEnum):
    """Temperature unit."""

    CELSIUS = 0
    FAHRENHEIT = 1


class AltitudeUnit(IntEnum):
    """Altitude unit."""

    METERS = 0
    FEET = 1


# Polling interval in seconds
DEFAULT_SCAN_INTERVAL = 15

# Level range
MIN_LEVEL = 1
MAX_LEVEL = 6

# Temperature range (Celsius)
MIN_TEMP_C = 8
MAX_TEMP_C = 36
