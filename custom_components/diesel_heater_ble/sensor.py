"""Sensor platform for Diesel Heater BLE."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricPotential, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ERROR_DESCRIPTIONS, ERROR_DESCRIPTIONS_DA
from .coordinator import DieselHeaterCoordinator
from .entity import DieselHeaterEntity


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
        # Use Danish descriptions if HA language is Danish
        lang = self.hass.config.language
        if lang == "da":
            description = ERROR_DESCRIPTIONS_DA.get(error_code, "Ukendt fejl")
        else:
            description = ERROR_DESCRIPTIONS.get(error_code, "Unknown error")
        return {"description": description}
