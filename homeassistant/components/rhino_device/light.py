"""This module contains the Rhino light entity."""

from homeassistant.components.light import LightEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import RhinoDeviceCoordinator


class RhinoLightEntity(LightEntity, CoordinatorEntity):
    """Representation of a Rhino light."""

    def __init__(self, coordinator: RhinoDeviceCoordinator, device_id: str) -> None:
        """Initialize the light entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"Rhino Light {device_id}"
        self._attr_unique_id = f"rhino_light_{device_id}"
        self._attr_is_on = False
        self._attr_brightness = 0
