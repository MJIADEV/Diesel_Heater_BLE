"""Config flow for Diesel Heater BLE integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS

from .const import DOMAIN, SERVICE_UUID

_LOGGER = logging.getLogger(__name__)


class DieselHeaterBLEConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Diesel Heater BLE."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle the bluetooth discovery step."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {
            "name": discovery_info.name or discovery_info.address
        }

        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm discovery."""
        if user_input is None:
            return self.async_show_form(
                step_id="bluetooth_confirm",
                description_placeholders={
                    "name": self._discovery_info.name or self._discovery_info.address
                },
            )

        return self.async_create_entry(
            title=self._discovery_info.name or "Diesel Heater",
            data={CONF_ADDRESS: self._discovery_info.address},
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user step to pick discovered device."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()

            discovery_info = self._discovered_devices[address]
            return self.async_create_entry(
                title=discovery_info.name or "Diesel Heater",
                data={CONF_ADDRESS: address},
            )

        # Discover devices
        self._discovered_devices = {}
        for discovery_info in async_discovered_service_info(self.hass):
            # Check if device has our service UUID
            if SERVICE_UUID.lower() in [
                s.lower() for s in discovery_info.service_uuids
            ]:
                self._discovered_devices[discovery_info.address] = discovery_info

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        # Build selection list
        device_options = {
            address: f"{info.name or 'Unknown'} ({address})"
            for address, info in self._discovered_devices.items()
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_ADDRESS): vol.In(device_options)}
            ),
        )
