"""Base entity for Diesel Heater BLE."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DieselHeaterCoordinator


class DieselHeaterEntity(CoordinatorEntity[DieselHeaterCoordinator]):
    """Base entity for diesel heater."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DieselHeaterCoordinator,
        unique_id_suffix: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.address}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
            name=coordinator.name,
            manufacturer="Generic",
            model="Diesel Parking Heater",
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self.coordinator.data is not None
