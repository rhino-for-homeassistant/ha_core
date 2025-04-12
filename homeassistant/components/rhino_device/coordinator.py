"""Coordinator for Rhino Devices"""

from datetime import timedelta
import logging

import async_timeout

from homeassistant.components.light import LightEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN
from .api import RhinoDeviceHub

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the coordinator for the Rhino Device."""
    # We're assuming that the API object is stored in the config entry. This probably needs to be set up during the config flow.
    my_api = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = RhinoDeviceCoordinator(hass, config_entry)

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()
    async_add_entities(
        RhinoDeviceEntity(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    )


class RhinoDeviceCoordinator(DataUpdateCoordinator):
    """Coordinator for the Rhino Device."""

    def __init__(self, hass, config_entry, my_api):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Rhino Light",
            config_entry=config_entry,
            update_interval=timedelta(seconds=30),
            always_update=True,
        )
        self.api = my_api
        self._device = None

    async def _async_setup(self):
        """Set up the coordinator.

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        self._device = await self.my_api.get_device()

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            async with async_timeout.timeout(10):
                # Fetch data from the API
                data = await self.api.get_data()
                # Process data if needed
                return data
        except Exception as e:
            _LOGGER.error("Error fetching data from API: %s", e)
            raise UpdateFailed(f"Error fetching data from API: {e}") from e


class RhinoDeviceEntity(CoordinatorEntity, LightEntity):
    pass
