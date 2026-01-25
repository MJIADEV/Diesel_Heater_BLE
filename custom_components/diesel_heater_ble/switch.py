"""Switch platform for Diesel Heater BLE."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DieselHeaterCoordinator
from .entity import DieselHeaterEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator: DieselHeaterCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DieselHeaterSwitch(coordinator)])


class DieselHeaterSwitch(DieselHeaterEntity, SwitchEntity):
    """Switch to control heater power."""

    _attr_name = "Power"
    _attr_icon = "mdi:fire"

    def __init__(self, coordinator: DieselHeaterCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, "power")

    @property
    def is_on(self) -> bool | None:
        """Return True if heater is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the heater."""
        if self.coordinator.data is None or not self.coordinator.data.is_on:
            await self.coordinator.async_toggle_power()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the heater."""
        if self.coordinator.data is not None and self.coordinator.data.is_on:
            await self.coordinator.async_toggle_power()
