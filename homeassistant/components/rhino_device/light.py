"""This module contains the Rhino light entity."""

from homeassistant.components.light import LightEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import RhinoDeviceCoordinator


class RhinoLightEntity(LightEntity, CoordinatorEntity[RhinoDeviceCoordinator]):
    """Representation of a Rhino light using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    def __init__(self, coordinator: RhinoDeviceCoordinator, device_id: str) -> None:
        """Initialize the light entity."""

        super().__init__(coordinator, context=device_id)
        self._device_id = device_id
        self._attr_name = f"Rhino Light {device_id}"
        self._attr_unique_id = f"rhino_light_{device_id}"
        self._attr_is_on = False
        self._attr_brightness = 0

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data[self._device_id][
            "state"
        ]  # Assume for now that this holds the on/off state
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        """Turn the light on.

        Example method how to request data updates.
        """
        # Do the turning on.
        # ...

        # Update the data
        await self.coordinator.async_request_refresh()
