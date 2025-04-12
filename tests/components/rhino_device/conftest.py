"""Common fixtures for the Rhino for HomeAssistant tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "homeassistant.components.rhino_device.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry
