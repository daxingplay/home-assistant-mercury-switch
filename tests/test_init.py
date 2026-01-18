"""Test integration setup and unload."""

from unittest.mock import MagicMock

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mercury_switch.const import DOMAIN


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Create a mock config entry."""
    return MockConfigEntry(
        version=1,
        domain=DOMAIN,
        title="SG108Pro (192.168.1.100)",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "test",
        },
        unique_id="sg108pro_192_168_1_100",
        entry_id="test_entry_id",
    )


async def test_setup_entry_success(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_mercury_switch_api: MagicMock,
) -> None:
    """Test successful integration setup."""
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert mock_config_entry.unique_id == "sg108pro_192_168_1_100"


async def test_setup_entry_login_failure(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_mercury_switch_api_auth_fail: MagicMock,
) -> None:
    """Test integration setup with login failure."""
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_unload_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_mercury_switch_api: MagicMock,
) -> None:
    """Test integration unload."""
    mock_config_entry.add_to_hass(hass)

    # Setup first
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED

    # Then unload
    await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
