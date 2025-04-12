"""Contains Rhino light entity definition and setup."""

import logging
from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RhinoDeviceCoordinator


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict[str, Any],
    async_add_entities: AddEntitiesCallback,
    discovery_info: dict[str, Any] | None = None,
) -> None:
    """Set up the Rhino light platform.

    This method is only for backwards compatibility.
    """
    # Use platform setup only if coordinator is already registered
    if DOMAIN not in hass.data or "coordinator" not in hass.data[DOMAIN]:
        return

    coordinator = hass.data[DOMAIN]["coordinator"]
    await coordinator.async_config_entry_first_refresh()
    _add_entities(coordinator, async_add_entities)


def _add_entities(
    coordinator: RhinoDeviceCoordinator, async_add_entities: AddEntitiesCallback
) -> None:
    """Add light entities for each Rhino device."""
    lights = [
        RhinoLightEntity(coordinator, device_id) for device_id in coordinator.data
    ]
    async_add_entities(lights)


class RhinoLightEntity(LightEntity, CoordinatorEntity[RhinoDeviceCoordinator]):
    """Representation of a Rhino light using CoordinatorEntity."""

    _attr_has_entity_name = True
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(self, coordinator: RhinoDeviceCoordinator, device_id: str) -> None:
        """Initialize the light entity."""
        logging.warning(f"Making light entity for {device_id}")
        super().__init__(coordinator, context=device_id)
        self._device_id = device_id
        self._attr_name = "Light"
        self._attr_unique_id = f"rhino_light_{device_id}"

        # Initialize state from coordinator data if available
        device_data = self.coordinator.data.get(self._device_id, {})
        self._attr_is_on = device_data.online
        self._attr_brightness = device_data.data.get("brightness", 0)

        # Set device info
        self._attr_device_info = device_data

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self._device_id not in self.coordinator.data:
            return

        device_data = self.coordinator.data[self._device_id]
        self._attr_is_on = device_data.get("state", self._attr_is_on)
        self._attr_brightness = device_data.get("brightness", self._attr_brightness)
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)

        # Call API to turn on the device
        await self.coordinator.api.turn_on(self._device_id, brightness=brightness)

        # Update entity state
        self._attr_is_on = True
        if brightness is not None:
            self._attr_brightness = brightness

        # Request refresh to confirm changes
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        # Call API to turn off the device
        await self.coordinator.api.turn_off(self._device_id)

        # Update entity state
        self._attr_is_on = False

        # Request refresh to confirm changes
        await self.coordinator.async_request_refresh()
