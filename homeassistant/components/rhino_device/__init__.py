"""The Rhino for HomeAssistant integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import RhinoDeviceHub

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
_PLATFORMS: list[Platform] = [Platform.LIGHT]

# TODO Create ConfigEntry type alias with API object
# TODO Rename type alias and update all entry annotations
type RhinoConfigEntry = ConfigEntry[RhinoDeviceHub]


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: RhinoConfigEntry) -> bool:
    """Set up Rhino for HomeAssistant from a config entry."""

    # TODO 1. Create API instance
    my_api = RhinoDeviceHub(entry.data["host"], hass)

    # TODO 2. Validate the API connection (and authentication)

    # TODO 3. Store an API object for your platforms to access
    entry.runtime_data = my_api

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


# TODO Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
