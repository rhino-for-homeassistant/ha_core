"""Coordinator for Rhino Devices."""

import asyncio
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RhinoDeviceHub

_LOGGER = logging.getLogger(__name__)


class RhinoDeviceCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for the Rhino Device."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry | None,
        my_api: RhinoDeviceHub,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Rhino Light",
            # Only attach config_entry if we have one (not for YAML)
            **({"config_entry": config_entry} if config_entry else {}),
            update_interval=timedelta(seconds=30),
            always_update=True,
        )
        self.api: RhinoDeviceHub = my_api
        self.devices = []
        self.data = {}

    async def _async_setup(self):
        """Set up the coordinator.

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        self.devices = await self.api.get_devices()
        self.data = {d.id: d for d in self.devices}

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            async with asyncio.timeout(10):
                # Fetch data from the API
                if not self.data:
                    return await self.api.get_initial_data()

                # If we haven't loaded devices yet, do so now
                if not self.devices:
                    self.devices = await self.api.get_devices()
                    if not self.devices:
                        _LOGGER.debug("No devices found during update")
                        return {}

                return await self.api.update(current_data=self.data)

        except Exception as err:
            _LOGGER.debug("Error fetching data from API: %s", err)
            raise UpdateFailed("Error communicating with API") from err
