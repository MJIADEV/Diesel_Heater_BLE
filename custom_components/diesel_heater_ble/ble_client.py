"""BLE client for Diesel Heater communication."""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from bleak import BleakClient
from bleak.exc import BleakError

from .const import (
    NOTIFY_CHARACTERISTIC_UUID,
    RESPONSE_HEADER,
    RESPONSE_LENGTH,
    SERVICE_UUID,
    WRITE_CHARACTERISTIC_UUID,
    AltitudeUnit,
    ControlMode,
    OperatingMode,
    RunningState,
    TemperatureUnit,
)
from .models import HeaterState

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice

_LOGGER = logging.getLogger(__name__)


class DieselHeaterBLEClient:
    """BLE client for communicating with diesel heater."""

    def __init__(self, ble_device: BLEDevice) -> None:
        """Initialize the BLE client."""
        self._ble_device = ble_device
        self._client: BleakClient | None = None
        self._response_data: bytes | None = None
        self._response_event = asyncio.Event()
        self._lock = asyncio.Lock()

    @property
    def address(self) -> str:
        """Return BLE device address."""
        return self._ble_device.address

    @property
    def is_connected(self) -> bool:
        """Return True if connected."""
        return self._client is not None and self._client.is_connected

    def set_ble_device(self, ble_device: BLEDevice) -> None:
        """Update BLE device reference without disconnecting."""
        self._ble_device = ble_device

    async def connect(self) -> bool:
        """Connect to the heater."""
        if self.is_connected:
            return True

        try:
            self._client = BleakClient(
                self._ble_device,
                disconnected_callback=self._on_disconnect,
            )
            await self._client.connect()

            # Subscribe to notifications
            await self._client.start_notify(
                NOTIFY_CHARACTERISTIC_UUID,
                self._notification_handler,
            )

            _LOGGER.debug("Connected to %s", self.address)
            return True
        except BleakError as err:
            _LOGGER.error("Failed to connect to %s: %s", self.address, err)
            self._client = None
            return False

    async def disconnect(self) -> None:
        """Disconnect from the heater."""
        if self._client is not None:
            try:
                await self._client.disconnect()
            except BleakError as err:
                _LOGGER.debug("Error during disconnect: %s", err)
            finally:
                self._client = None

    def _on_disconnect(self, client: BleakClient) -> None:
        """Handle disconnection."""
        _LOGGER.debug("Disconnected from %s", self.address)
        self._client = None

    def _notification_handler(
        self, sender: int, data: bytearray  # noqa: ARG002
    ) -> None:
        """Handle notification data from heater."""
        _LOGGER.debug("Received notification: %s", data.hex())
        self._response_data = bytes(data)
        self._response_event.set()

    async def send_command(
        self, command: bytes, wait_response: bool = True, timeout: float = 5.0
    ) -> bytes | None:
        """Send a command and optionally wait for response."""
        async with self._lock:
            if not self.is_connected:
                if not await self.connect():
                    return None

            self._response_event.clear()
            self._response_data = None

            try:
                _LOGGER.debug("Sending command: %s", command.hex())
                await self._client.write_gatt_char(
                    WRITE_CHARACTERISTIC_UUID,
                    command,
                    response=False,
                )

                if wait_response:
                    try:
                        await asyncio.wait_for(
                            self._response_event.wait(),
                            timeout=timeout,
                        )
                        return self._response_data
                    except asyncio.TimeoutError:
                        _LOGGER.warning("Timeout waiting for response")
                        return None
                return None
            except BleakError as err:
                _LOGGER.error("Failed to send command: %s", err)
                return None

    @staticmethod
    def calculate_checksum(data: bytes) -> int:
        """Calculate checksum for command/response."""
        return sum(data) % 256

    @staticmethod
    def build_command(cmd_type: int, cmd_code: int, param: int = 0) -> bytes:
        """Build a command with proper header and checksum."""
        cmd = bytes([
            0xBA,
            0xAB,
            0x04,
            cmd_type,
            cmd_code,
            (param >> 8) & 0xFF,
            param & 0xFF,
        ])
        checksum = DieselHeaterBLEClient.calculate_checksum(cmd)
        return cmd + bytes([checksum])

    @staticmethod
    def parse_response(data: bytes) -> HeaterState | None:
        """Parse a 21-byte response into HeaterState."""
        if data is None or len(data) < RESPONSE_LENGTH:
            _LOGGER.warning("Invalid response length: %s", len(data) if data else 0)
            return None

        # Verify header
        if data[:4] != RESPONSE_HEADER:
            _LOGGER.warning("Invalid response header: %s", data[:4].hex())
            return None

        # Verify checksum
        expected_checksum = DieselHeaterBLEClient.calculate_checksum(data[:20])
        if data[20] != expected_checksum:
            _LOGGER.warning(
                "Checksum mismatch: got %02x, expected %02x",
                data[20],
                expected_checksum,
            )
            # Continue anyway - some devices may have checksum issues

        # Parse fields
        try:
            operating_mode = OperatingMode(data[4])
        except ValueError:
            operating_mode = OperatingMode.IDLE

        try:
            control_mode = ControlMode(data[5])
        except ValueError:
            control_mode = ControlMode.LEVEL

        level_or_target = data[6]

        try:
            running_state = RunningState(data[7])
        except ValueError:
            running_state = RunningState.IDLE

        auto_mode = data[8] == 1
        supply_voltage = data[9]

        try:
            temperature_unit = TemperatureUnit(data[10])
        except ValueError:
            temperature_unit = TemperatureUnit.CELSIUS

        environment_temp = data[11] - 30  # Convert to Celsius

        # Combustion temp is big-endian 16-bit
        combustion_temp = (data[12] << 8) | data[13]

        try:
            altitude_unit = AltitudeUnit(data[14])
        except ValueError:
            altitude_unit = AltitudeUnit.METERS

        high_altitude_mode = data[15] == 1

        # Altitude is big-endian 16-bit
        altitude = (data[16] << 8) | data[17]

        return HeaterState(
            operating_mode=operating_mode,
            control_mode=control_mode,
            level_or_target=level_or_target,
            running_state=running_state,
            auto_mode=auto_mode,
            supply_voltage=supply_voltage,
            temperature_unit=temperature_unit,
            environment_temp=environment_temp,
            combustion_temp=combustion_temp,
            altitude_unit=altitude_unit,
            high_altitude_mode=high_altitude_mode,
            altitude=altitude,
        )
