"""Our API for the Rhino Device interactions goes here."""

from dataclasses import dataclass
import logging
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant


@dataclass
class RhinoDeviceSate:
    """Rhino Device state."""

    id: str
    name: str
    online: bool
    data: dict[str, Any]
    # Brightness
    # RGB
    # On/off


class RhinoDeviceHub:
    """Rhino Device Hub."""

    def __init__(self, host: str, hass: HomeAssistant) -> None:
        """Initialize the Rhino Device Hub."""
        self._host = host
        self._hass = hass
        self._name = host
        self._id = host
        self.devices = []
        self.online = True

    async def connect(self) -> bool:
        """Connect to the Rhino device."""
        # Implement your connection logic here
        try:
            # Example connection code
            # self._client = await self._create_connection()
            return True
        except Exception as ex:
            logging.error("Failed to connect to Rhino device: %s", ex)
            raise

    async def disconnect(self) -> None:
        """Disconnect from the Rhino device."""
        # Implement your disconnection logic here
        # if self._client:
        #     await self._client.close()

    async def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with the Rhino Device."""
        # Placeholder for authentication logic
        return True

    async def get_devices(self) -> list[RhinoDeviceSate]:
        """Get the device information."""
        # Placeholder for getting device information
        sample_devices: list[RhinoDeviceSate] = [
            RhinoDeviceSate(
                id="light1",
                name="Rhino Device 1",
                online=True,
                data={"rgb_color": "255,0,0", "brightness": 255},
            ),
            RhinoDeviceSate(
                id="light2",
                name="Rhino Device 2",
                online=False,
                data={"rgb_color": "0,255,0", "brightness": 255},
            ),
        ]
        return sample_devices

    async def get_initial_data(self):
        """Get the initial data from the device."""
        # Placeholder for getting initial data
        return {"initial_data": "Rhino"}

    async def update(self, current_data):
        """Update the device data."""
        # Placeholder for updating device data
        return current_data

    async def turn_on(self, device_id, brightness):
        url = f"http://localhost:8021/device{device_id}/on"
        payload = {
            "brightness": "{brightness}",
        }

        async with (
            aiohttp.ClientSession() as session,
            session.post(url, json=payload, timeout=5) as resp,
        ):
            if resp.status != 200:
                logging.error(
                    "Unexpected status response from %s: %s",
                    url,
                    resp.status,
                )  # TODO does this logging work?
                return self.async_abort(reason="unexpected_status_code")
            return None

    async def turn_off(self, device_id):
        url = f"http://localhost:8000/device{device_id}/off"
        url = "http://localhost:8021/ping"
        payload = {
            "brightness": "{brightness}",
        }

        async with (
            aiohttp.ClientSession() as session,
            session.post(url, json=payload, timeout=5) as resp,
        ):
            if resp.status != 200:
                logging.error(
                    "Unexpected status response from %s: %s",
                    url,
                    resp.status,
                )
                text = await resp.text()
                logging.info(text)
                return self.async_abort(reason="unexpected_status_code")
            return None
