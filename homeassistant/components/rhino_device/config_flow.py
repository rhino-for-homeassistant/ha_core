"""Config flow for the Rhino for HomeAssistant integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
from light import AwesomeLight
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
    # )

    hub = PlaceholderHub(data[CONF_HOST])

    if not await hub.authenticate(data[CONF_USERNAME], data[CONF_PASSWORD]):
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "Name of the device"}


class LocalConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rhino for HomeAssistant."""

    VERSION = 1

    async def async_step_zeroconf(
        self, discovery_info: dict[str, Any]
    ) -> ConfigFlowResult:
        """Handle a device discovered via Zeroconf."""

        _LOGGER.debug("Zeroconf discovery received: %s", discovery_info)

        host = discovery_info["host"]
        port = discovery_info["port"]
        path = discovery_info["properties"].get("path", "/device")

        base_url = f"http://localhost:8000/{path}"
        status_url = f"{base_url}/status"

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(status_url, timeout=5) as resp,
            ):
                if resp.status != 200:
                    _LOGGER.warning(
                        "Unexpected status response from %s: %s",
                        status_url,
                        resp.status,
                    )
                    return self.async_abort(reason="unexpected_status_code")

                data = await resp.json()
                if data.get("device_type") != "rhino":
                    _LOGGER.debug("Device at %s is not a Rhino", status_url)
                    return self.async_abort(reason="not_rhino")

        except (TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error(
                "Could not connect to Rhino device at %s: %s", status_url, err
            )
            return self.async_abort(reason="cannot_connect")

        # Optional: generate unique ID based on host/path
        await self.async_set_unique_id(f"rhino_{host}_{path.strip('/')}")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"Rhino @ {host}",
            data={"host": host, "port": port, "path": path},
        )


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up Rhino light from YAML."""
    host = config["host"]
    port = config["port"]
    path = config["path"]

    async_add_entities([AwesomeLight(host, port, path)])

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class RhinoDeviceConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rhino Device."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

        # Create entry
        return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)

    async def async_step_import(self, import_info: dict[str, Any]) -> FlowResult:
        """Handle import from YAML config."""
        # Check if device is already configured
        await self.async_set_unique_id(import_info[CONF_HOST])
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"Imported {import_info[CONF_HOST]}", data=import_info
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
