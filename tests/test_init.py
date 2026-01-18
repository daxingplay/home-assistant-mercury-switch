"""Test integration setup and unload."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.mercury_switch import async_setup_entry, async_unload_entry
from custom_components.mercury_switch.const import DOMAIN


@pytest.fixture
def mock_config_entry() -> ConfigEntry:
    """Create a mock config entry."""
    return ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="SG108Pro (192.168.1.100)",
        data={
            CONF_HOST: "192.168.1.100",
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "test",
        },
        source="user",
        unique_id="sg108pro_192_168_1_100",
        options={},
        entry_id="test_entry_id",
    )


async def test_setup_entry_success(
    hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_mercury_switch_api
) -> None:
    """Test successful integration setup."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups",
        return_value=None,
    ) as mock_forward:
        result = await async_setup_entry(hass, mock_config_entry)

        assert result is True
        assert mock_config_entry.unique_id == "sg108pro_192_168_1_100"
        mock_forward.assert_called_once()


async def test_setup_entry_login_failure(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_mercury_switch_api_auth_fail,
) -> None:
    """Test integration setup with login failure."""
    mock_config_entry.add_to_hass(hass)

    with pytest.raises(ConfigEntryNotReady):
        await async_setup_entry(hass, mock_config_entry)


async def test_unload_entry(
    hass: HomeAssistant, mock_config_entry: ConfigEntry, mock_mercury_switch_api
) -> None:
    """Test integration unload."""
    mock_config_entry.add_to_hass(hass)

    # Setup first
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_forward_entry_setups",
        return_value=None,
    ):
        await async_setup_entry(hass, mock_config_entry)

    # Then unload
    with patch(
        "homeassistant.config_entries.ConfigEntries.async_unload_platforms",
        return_value=True,
    ) as mock_unload:
        result = await async_unload_entry(hass, mock_config_entry)

        assert result is True
        mock_unload.assert_called_once()
