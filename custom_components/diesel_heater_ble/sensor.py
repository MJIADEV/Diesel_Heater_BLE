"""Sensor platform for Diesel Heater BLE."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricPotential, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DieselHeaterCoordinator
from .entity import DieselHeaterEntity

_LOGGER = logging.getLogger(__name__)

# Cache for loaded translations
_translations_cache: dict[str, dict[str, str]] = {}


def get_error_description(language: str, error_code: int) -> str:
    """Get error description from translation files."""
    global _translations_cache

    # Default to English if language not supported
    if language not in ("en", "da"):
        language = "en"

    # Load translations if not cached
    if language not in _translations_cache:
        translations_path = Path(__file__).parent / "translations" / f"{language}.json"
        try:
            with open(translations_path, encoding="utf-8") as f:
                data = json.load(f)
                _translations_cache[language] = data.get("error_descriptions", {})
        except (OSError, json.JSONDecodeError) as err:
            _LOGGER.warning("Failed to load translations for %s: %s", language, err)
            _translations_cache[language] = {}

    # Get description
    descriptions = _translations_cache.get(language, {})
    return descriptions.get(str(error_code), descriptions.get("unknown", "Unknown error"))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: DieselHeaterCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        DieselHeaterVoltageSensor(coordinator),
        DieselHeaterEnvironmentTempSensor(coordinator),
        DieselHeaterCombustionTempSensor(coordinator),
        DieselHeaterRunningStateSensor(coordinator),
        DieselHeaterOperatingModeSensor(coordinator),
    ]

    # Add error code sensor if in error state
    entities.append(DieselHeaterErrorCodeSensor(coordinator))

    async_add_entities(entities)


class DieselHeaterVoltageSensor(DieselHeaterEntity, SensorEntity):
    """Sensor for supply voltage."""

    _attr_translation_key = "voltage"
    _attr_device_class = SensorDeviceClass.VOLTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT

    def __init__(self, coordinator: DieselHeaterCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "voltage")

    @property
    def native_value(self) -> int | None:
        """Return the voltage."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.supply_voltage


class DieselHeaterEnvironmentTempSensor(DieselHeaterEntity, SensorEntity):
    """Sensor for environment temperature."""

    _attr_translation_key = "environment_temp"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: DieselHeaterCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "environment_temp")

    @property
    def native_value(self) -> int | None:
        """Return the temperature."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.environment_temp


class DieselHeaterCombustionTempSensor(DieselHeaterEntity, SensorEntity):
    """Sensor for combustion chamber temperature."""

    _attr_translation_key = "combustion_temp"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: DieselHeaterCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "combustion_temp")

    @property
    def native_value(self) -> int | None:
        """Return the temperature."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.combustion_temp


class DieselHeaterRunningStateSensor(DieselHeaterEntity, SensorEntity):
    """Sensor for running state."""

    _attr_translation_key = "running_state"
    _attr_icon = "mdi:state-machine"

    def __init__(self, coordinator: DieselHeaterCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "running_state")

    @property
    def native_value(self) -> str | None:
        """Return the running state."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.running_state_text


class DieselHeaterOperatingModeSensor(DieselHeaterEntity, SensorEntity):
    """Sensor for operating mode."""

    _attr_translation_key = "operating_mode"
    _attr_icon = "mdi:thermostat"

    def __init__(self, coordinator: DieselHeaterCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "operating_mode")

    @property
    def native_value(self) -> str | None:
        """Return the operating mode."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.operating_mode_text


class DieselHeaterErrorCodeSensor(DieselHeaterEntity, SensorEntity):
    """Sensor for error code."""

    _attr_translation_key = "error_code"
    _attr_icon = "mdi:alert-circle"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: DieselHeaterCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, "error_code")

    @property
    def native_value(self) -> str | None:
        """Return the error code with E prefix."""
        if self.coordinator.data is None:
            return None
        error_code = self.coordinator.data.error_code
        if error_code is None:
            return None
        return f"E{error_code}"

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return error description as attribute."""
        if self.coordinator.data is None:
            return None
        error_code = self.coordinator.data.error_code
        if error_code is None:
            return None
        # Get description from translation files based on HA language
        language = self.hass.config.language
        description = get_error_description(language, error_code)
        return {"description": description}
