"""Data models for Diesel Heater BLE integration."""
from dataclasses import dataclass

from .const import (
    AltitudeUnit,
    ControlMode,
    OperatingMode,
    RunningState,
    TemperatureUnit,
)


@dataclass
class HeaterState:
    """Represents the current state of the diesel heater."""

    operating_mode: OperatingMode
    control_mode: ControlMode
    level_or_target: int  # Level (1-6) or target temp depending on control_mode
    running_state: RunningState
    auto_mode: bool
    supply_voltage: int  # Whole volts
    temperature_unit: TemperatureUnit
    environment_temp: int  # Celsius (raw value - 30)
    combustion_temp: int  # Celsius
    altitude_unit: AltitudeUnit
    high_altitude_mode: bool
    altitude: int

    @property
    def is_on(self) -> bool:
        """Return True if heater is running."""
        return self.operating_mode != OperatingMode.IDLE

    @property
    def is_heating(self) -> bool:
        """Return True if actively heating."""
        return self.running_state == RunningState.HEATING

    @property
    def is_error(self) -> bool:
        """Return True if in error state."""
        return self.control_mode == ControlMode.ERROR

    @property
    def error_code(self) -> int | None:
        """Return error code if in error state."""
        if self.is_error:
            return self.level_or_target
        return None

    @property
    def level(self) -> int | None:
        """Return current level if in level mode."""
        if self.control_mode == ControlMode.LEVEL and not self.is_error:
            return self.level_or_target
        return None

    @property
    def target_temperature(self) -> int | None:
        """Return target temperature if in temperature mode."""
        if self.control_mode == ControlMode.TEMPERATURE:
            return self.level_or_target
        return None

    @property
    def running_state_text(self) -> str:
        """Return human-readable running state."""
        state_map = {
            RunningState.IDLE: "Idle",
            RunningState.COOLING: "Cooling Down",
            RunningState.GLOWPLUG: "Glow Plug",
            RunningState.HEATING: "Heating",
            RunningState.PREHEATING: "Preheating",
        }
        return state_map.get(self.running_state, f"Unknown ({self.running_state})")

    @property
    def operating_mode_text(self) -> str:
        """Return human-readable operating mode."""
        mode_map = {
            OperatingMode.IDLE: "Off",
            OperatingMode.HEATING: "Heating",
            OperatingMode.COOLING: "Cooling",
            OperatingMode.FAN_ONLY: "Fan Only",
        }
        return mode_map.get(self.operating_mode, f"Unknown ({self.operating_mode})")
