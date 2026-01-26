"""Number platform for Diesel Heater BLE."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    MAX_LEVEL,
    MAX_TEMP_C,
    MIN_LEVEL,
    MIN_TEMP_C,
    ControlMode,
)
from .coordinator import DieselHeaterCoordinator
from .entity import DieselHeaterEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator: DieselHeaterCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        DieselHeaterLevelNumber(coordinator),
        DieselHeaterTemperatureNumber(coordinator),
    ])


class DieselHeaterLevelNumber(DieselHeaterEntity, NumberEntity):
    """Number for heater level."""

    _attr_translation_key = "level"
    _attr_icon = "mdi:speedometer"
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = MIN_LEVEL
    _attr_native_max_value = MAX_LEVEL
    _attr_native_step = 1

    def __init__(self, coordinator: DieselHeaterCoordinator) -> None:
        """Initialize the number."""
        super().__init__(coordinator, "level")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if not super().available:
            return False
        # Only available in level mode
        return self.coordinator.data.control_mode == ControlMode.LEVEL

    @property
    def native_value(self) -> float | None:
        """Return the current level."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.level

    async def async_set_native_value(self, value: float) -> None:
        """Set the level."""
        await self.coordinator.async_set_level(int(value))


class DieselHeaterTemperatureNumber(DieselHeaterEntity, NumberEntity):
    """Number for target temperature."""

    _attr_translation_key = "temperature"
    _attr_icon = "mdi:thermometer"
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = MIN_TEMP_C
    _attr_native_max_value = MAX_TEMP_C
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: DieselHeaterCoordinator) -> None:
        """Initialize the number."""
        super().__init__(coordinator, "temperature")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if not super().available:
            return False
        # Only available in temperature mode
        return self.coordinator.data.control_mode == ControlMode.TEMPERATURE

    @property
    def native_value(self) -> float | None:
        """Return the target temperature."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.target_temperature

    async def async_set_native_value(self, value: float) -> None:
        """Set the temperature."""
        await self.coordinator.async_set_temperature(int(value))
