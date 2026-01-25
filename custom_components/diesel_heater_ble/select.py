"""Select platform for Diesel Heater BLE."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ControlMode
from .coordinator import DieselHeaterCoordinator
from .entity import DieselHeaterEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    coordinator: DieselHeaterCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        DieselHeaterControlModeSelect(coordinator),
    ])


class DieselHeaterControlModeSelect(DieselHeaterEntity, SelectEntity):
    """Select for control mode."""

    _attr_name = "Control Mode"
    _attr_icon = "mdi:tune"
    _attr_options = ["Level", "Temperature"]

    def __init__(self, coordinator: DieselHeaterCoordinator) -> None:
        """Initialize the select."""
        super().__init__(coordinator, "control_mode")

    @property
    def current_option(self) -> str | None:
        """Return the current control mode."""
        if self.coordinator.data is None:
            return None
        if self.coordinator.data.control_mode == ControlMode.LEVEL:
            return "Level"
        if self.coordinator.data.control_mode == ControlMode.TEMPERATURE:
            return "Temperature"
        return None

    async def async_select_option(self, option: str) -> None:
        """Select control mode."""
        if option == "Level":
            await self.coordinator.async_set_level_mode()
        elif option == "Temperature":
            await self.coordinator.async_set_temp_mode()
