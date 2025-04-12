"""Config flow for Rhino Device integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Schema for user step
USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_PORT, default=80): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from USER_SCHEMA with values provided by the user.
    """
    host = data[CONF_HOST]
    port = data.get(CONF_PORT, 80)
    username = data[CONF_USERNAME]
    password = data[CONF_PASSWORD]

    base_url = f"http://{host}:{port}/device"
    status_url = f"{base_url}/status"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(status_url, timeout=5) as resp:
                if resp.status != 200:
                    raise CannotConnect(f"Unexpected status code: {resp.status}")

                device_data = await resp.json()

                if device_data.get("device_type") != "rhino":
                    raise CannotConnect("Device is not a Rhino device")

                # Now try to authenticate
                auth_url = f"{base_url}/auth"
                async with session.post(
                    auth_url,
                    json={"username": username, "password": password},
                    timeout=5,
                ) as auth_resp:
                    if auth_resp.status != 200:
                        raise InvalidAuth("Invalid authentication")

                    # If we get here, authentication was successful
                    auth_data = await auth_resp.json()

                    # Extract device name from the data if available
                    device_name = device_data.get("name", f"Rhino @ {host}")

                    return {
                        "title": device_name,
                        "device_id": device_data.get("id", host),
                    }
    except aiohttp.ClientError as err:
        raise CannotConnect(f"Connection error: {err}") from err
    except TimeoutError as err:
        raise CannotConnect("Connection timeout") from err


class RhinoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rhino Device."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_host: str | None = None
        self._discovered_port: int | None = None
        self._discovered_path: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                # Set unique ID to prevent duplicate entries
                await self.async_set_unique_id(f"rhino_{info['device_id']}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Use discovered values if available
        user_input_defaults = {}
        if self._discovered_host:
            user_input_defaults[CONF_HOST] = self._discovered_host
        if self._discovered_port:
            user_input_defaults[CONF_PORT] = self._discovered_port

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST, default=user_input_defaults.get(CONF_HOST, "")
                    ): str,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(
                        CONF_PORT, default=user_input_defaults.get(CONF_PORT, 80)
                    ): int,
                }
            ),
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle zeroconf discovery."""
        host = discovery_info.host
        port = discovery_info.port
        path = discovery_info.properties.get("path", "/device")

        # Store discovered values for use in user step
        self._discovered_host = host
        self._discovered_port = port
        self._discovered_path = path.strip("/")

        base_url = f"http://{host}:{port}{path}"
        status_url = f"{base_url}/status"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(status_url, timeout=5) as resp:
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
                        return self.async_abort(reason="not_rhino_device")

        except (TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error(
                "Could not connect to Rhino device at %s: %s", status_url, err
            )
            return self.async_abort(reason="cannot_connect")

        # Generate unique ID based on device ID if available, otherwise host/path
        device_id = data.get("id", f"{host}_{path.strip('/')}")
        await self.async_set_unique_id(f"rhino_{device_id}")
        self._abort_if_unique_id_configured()

        # Show the form to the user to complete configuration
        return await self.async_step_user()


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
