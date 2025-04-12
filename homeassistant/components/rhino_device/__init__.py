"""The Rhino for HomeAssistant integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import Event, HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.typing import ConfigType

from .api import RhinoDeviceHub
from .const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, DOMAIN
from .coordinator import RhinoDeviceCoordinator

_LOGGER = logging.getLogger(__name__)

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
_PLATFORMS: list[Platform] = [Platform.LIGHT]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


# TODO Create ConfigEntry type alias with API object
# TODO Rename type alias and update all entry annotations
class RhinoConfigEntry(ConfigEntry):
    """Configuration entry with runtime data for RhinoDeviceHub."""

    runtime_data: RhinoDeviceHub


# TODO Update entry annotation


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Rhino device component from YAML configuration."""
    if DOMAIN not in config:
        return True
    domain_config = config[DOMAIN]
    _LOGGER.warning(f"Domain config: {domain_config}")
    hass.data.setdefault(DOMAIN, {})

    # Create API instance from YAML config
    for entry_config in (
        domain_config if isinstance(domain_config, list) else [domain_config]
    ):
        # TODO 1. Create API instance
        my_api = RhinoDeviceHub(host=entry_config[CONF_HOST], hass=hass)
        # Store API for platform access
        hass.data[DOMAIN]["api"] = my_api

        # Create coordinator for YAML config
        # Create coordinator for YAML config
        coordinator = RhinoDeviceCoordinator(hass, None, my_api)

        print("Setup coordinator -- awaiting async refresh")
        await coordinator.async_refresh()
        print("Finished async refresh")
        hass.data[DOMAIN]["coordinator"] = coordinator

        # Register cleanup when Home Assistant stops
        async def _async_stop_rhino(_: Event) -> None:
            """Stop the Rhino connection."""
            await my_api.disconnect()

        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _async_stop_rhino)

        # Set up the platform via discovery
        for platform in _PLATFORMS:
            hass.async_create_task(
                async_load_platform(hass, platform, DOMAIN, {}, entry_config)
            )

    return True


# Implement this to prevent errors if config entries attempt to load
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Rhino from a config entry - not supported."""
    _LOGGER.warning(
        "Config entry setup attempted for Rhino device but only YAML configuration is supported"
    )
    return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True
