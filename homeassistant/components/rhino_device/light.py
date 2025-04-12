"""Contains Rhino light entity definition and setup."""

import logging
from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import RhinoDeviceState
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
        device_state: RhinoDeviceState = self.coordinator.data.get(self._device_id, {})
        device_data = device_state.data if device_state else {}
        self._attr_is_on = device_state.online & device_data.get("is_on", False)
        self._attr_brightness = device_data.get("brightness", 0)
        self._attr_rgb_color = device_data.get("rgb_color", None)
        self._attr_color_mode = (
            ColorMode.RGB
            if device_data.get("rgb_color", None)
            else ColorMode.BRIGHTNESS
        )

    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        return self._attr_brightness

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._attr_is_on

    @property
    def rgb_color(self) -> tuple[float, float, float] | None:
        """HS color of the light."""
        if self._device_control.can_set_color:
            hsbxy = self._device_data.hsb_xy_color
            hue = hsbxy[0] / (self._device_control.max_hue / 360)
            sat = hsbxy[1] / (self._device_control.max_saturation / 100)
            if hue is not None and sat is not None:
                return hue, sat
        return None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self._device_id not in self.coordinator.data:
            return

        device_state: RhinoDeviceState = self.coordinator.data.get(self._device_id, {})
        device_data = device_state.data if device_state else {}
        self._attr_is_on = device_state.online & device_data.get("is_on", False)
        self._attr_brightness = device_data.get("brightness", self.brightness)
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS) | self.brightness

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
