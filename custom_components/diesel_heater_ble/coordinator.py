"""DataUpdateCoordinator for Diesel Heater BLE."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .ble_client import DieselHeaterBLEClient
from .const import (
    CMD_GET_STATUS,
    CMD_PRESS_DOWN,
    CMD_PRESS_UP,
    CMD_SET_FAN_MODE,
    CMD_SET_LEVEL_MODE,
    CMD_SET_TEMP_MODE,
    CMD_TOGGLE_POWER,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ControlMode,
)
from .models import HeaterState

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice

_LOGGER = logging.getLogger(__name__)


class DieselHeaterCoordinator(DataUpdateCoordinator[HeaterState | None]):
    """Coordinator for diesel heater BLE updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        ble_device: BLEDevice,
        name: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self._ble_device = ble_device
        self._client = DieselHeaterBLEClient(ble_device)
        self._address = ble_device.address

    @property
    def address(self) -> str:
        """Return device address."""
        return self._address

    def update_ble_device(self, ble_device: BLEDevice) -> None:
        """Update the BLE device reference."""
        self._ble_device = ble_device
        self._client = DieselHeaterBLEClient(ble_device)

    async def _async_update_data(self) -> HeaterState | None:
        """Fetch data from heater."""
        # Try to get fresh BLE device from scanner
        if device := bluetooth.async_ble_device_from_address(
            self.hass, self._address, connectable=True
        ):
            if device != self._ble_device:
                self.update_ble_device(device)

        response = await self._client.send_command(CMD_GET_STATUS)
        if response is None:
            raise UpdateFailed("Failed to get status from heater")

        state = DieselHeaterBLEClient.parse_response(response)
        if state is None:
            raise UpdateFailed("Failed to parse heater response")

        return state

    async def async_toggle_power(self) -> bool:
        """Toggle heater power."""
        response = await self._client.send_command(CMD_TOGGLE_POWER)
        if response is not None:
            await self.async_request_refresh()
            return True
        return False

    async def async_set_fan_mode(self) -> bool:
        """Set fan-only mode."""
        response = await self._client.send_command(CMD_SET_FAN_MODE)
        if response is not None:
            await self.async_request_refresh()
            return True
        return False

    async def async_set_level_mode(self) -> bool:
        """Set level control mode."""
        if self.data and self.data.control_mode == ControlMode.LEVEL:
            return True  # Already in level mode
        response = await self._client.send_command(CMD_SET_LEVEL_MODE)
        if response is not None:
            await self.async_request_refresh()
            return True
        return False

    async def async_set_temp_mode(self) -> bool:
        """Set temperature control mode."""
        if self.data and self.data.control_mode == ControlMode.TEMPERATURE:
            return True  # Already in temp mode
        response = await self._client.send_command(CMD_SET_TEMP_MODE)
        if response is not None:
            await self.async_request_refresh()
            return True
        return False

    async def async_press_up(self) -> bool:
        """Press up button (increase level/temp)."""
        response = await self._client.send_command(CMD_PRESS_UP)
        if response is not None:
            await self.async_request_refresh()
            return True
        return False

    async def async_press_down(self) -> bool:
        """Press down button (decrease level/temp)."""
        response = await self._client.send_command(CMD_PRESS_DOWN)
        if response is not None:
            await self.async_request_refresh()
            return True
        return False

    async def async_set_level(self, target_level: int) -> bool:
        """Set heater level (1-6)."""
        if self.data is None:
            return False

        current = self.data.level
        if current is None:
            # Not in level mode, switch first
            if not await self.async_set_level_mode():
                return False
            await self.async_request_refresh()
            if self.data is None or self.data.level is None:
                return False
            current = self.data.level

        delta = target_level - current
        if delta == 0:
            return True

        # Send up/down presses to reach target
        command = CMD_PRESS_UP if delta > 0 else CMD_PRESS_DOWN
        for _ in range(abs(delta)):
            response = await self._client.send_command(command)
            if response is None:
                return False

        await self.async_request_refresh()
        return True

    async def async_set_temperature(self, target_temp: int) -> bool:
        """Set target temperature."""
        if self.data is None:
            return False

        current = self.data.target_temperature
        if current is None:
            # Not in temp mode, switch first
            if not await self.async_set_temp_mode():
                return False
            await self.async_request_refresh()
            if self.data is None or self.data.target_temperature is None:
                return False
            current = self.data.target_temperature

        delta = target_temp - current
        if delta == 0:
            return True

        # Send up/down presses to reach target
        command = CMD_PRESS_UP if delta > 0 else CMD_PRESS_DOWN
        for _ in range(abs(delta)):
            response = await self._client.send_command(command)
            if response is None:
                return False

        await self.async_request_refresh()
        return True

    async def async_shutdown(self) -> None:
        """Disconnect from device."""
        await self._client.disconnect()
