"""Our API for the Rhino Device interactions goes here."""

from dataclasses import dataclass
import logging
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant

from .const import MODE


@dataclass
class RhinoDeviceState:
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

    test_data = {} if MODE == "test" else None

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

    async def get_devices(self) -> list[RhinoDeviceState]:
        """Get the device information."""
        # Placeholder for getting device information
        sample_devices: list[RhinoDeviceState] = [
            RhinoDeviceState(
                id="light1",
                name="Rhino Device 1",
                online=True,
                data={"is_on": True, "rgb_color": [255, 0, 0], "brightness": 255},
            ),
            RhinoDeviceState(
                id="light2",
                name="Rhino Device 2",
                online=True,
                data={"is_on": False, "rgb_color": [0, 255, 0], "brightness": 255},
            ),
        ]
        return sample_devices

    async def get_initial_data(self):
        """Get the initial data from the device."""
        # Placeholder for getting initial data
        sample_devices: list[RhinoDeviceState] = [
            RhinoDeviceState(
                id="light1",
                name="Rhino Device 1",
                online=True,
                data={"is_on": True, "rgb_color": [255, 0, 0], "brightness": 255},
            ),
            RhinoDeviceState(
                id="light2",
                name="Rhino Device 2",
                online=True,
                data={"is_on": False, "rgb_color": [0, 255, 0], "brightness": 255},
            ),
        ]

        if MODE == "test":
            # In test mode, we don't actually get the device data
            # but just return the test data
            self.test_data = {s.id: s for s in sample_devices}

        return {s.id: s for s in sample_devices}

    async def update(self, current_data):
        if MODE == "test":
            # In test mode, we don't actually update the device
            # but just simulate the action
            print(f"Simulating update with current data: {current_data}")
            return self.test_data
        # Placeholder for updating device data
        # FETCH DATA FROM DEVICE

        return current_data

    async def turn_on(self, device_id, brightness):
        if MODE == "test":
            # In test mode, we don't actually turn on the device
            # but just simulate the action
            print(
                f"Simulating turning on device {device_id} with brightness {brightness}"
            )
            # Update test_data with new brightness and status

            self.test_data[device_id].data["is_on"] = True
            self.test_data[device_id].data["brightness"] = brightness

            return None

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
        if MODE == "test":
            # In test mode, we don't actually turn on the device
            # but just simulate the action
            print(f"Simulating turning off device {device_id}")

            # Update test_data with new brightness and status
            self.test_data[device_id].data["is_on"] = False
            self.test_data[device_id].data["brightness"] = 0

            return None
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

    async def set_brightness(self, device_id, brightness):
        if MODE == "test":
            # In test mode, we don't actually turn on the device
            # but just simulate the action
            print(
                f"Simulating setting brightness of device {device_id} to {brightness}"
            )
            # Update test_data with new brightness and status
            self.test_data[device_id].data["brightness"] = brightness
            self.test_data[device_id].data["is_on"] = True

            return None

        url = f"http://localhost:8000/device{device_id}/brightness"
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
                return self.async_abort(reason="unexpected_status_code")
            return None

    async def set_rgb_color(self, device_id, rgb_color):
        if MODE == "test":
            # In test mode, we don't actually turn on the device
            # but just simulate the action
            print(f"Simulating setting RGB color of device {device_id} to {rgb_color}")

            # Update test data with new RGB color
            self.test_data[device_id].data["rgb_color"] = rgb_color

            return None

        url = f"http://localhost:8000/device{device_id}/color"
        payload = {
            "rgb_color": "{rgb_color}",
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
                return self.async_abort(reason="unexpected_status_code")
            return None
