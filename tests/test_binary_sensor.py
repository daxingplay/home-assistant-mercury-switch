"""Test binary sensor entities for Mercury Switch integration."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mercury_switch.binary_sensor import async_setup_entry
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


@pytest.fixture
def mock_switch_infos():
    """Mock switch information data."""
    return {
        "port_1_status": "on",
        "port_2_status": "off",
        "port_3_status": "off",
        "port_4_status": "on",
        "port_5_status": "off",
        "port_6_status": "off",
        "port_7_status": "on",
        "port_8_status": "off",
    }


async def test_binary_sensor_entities_created(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_mercury_switch_api,
    mock_switch_infos,
) -> None:
    """Test that binary sensor entities are created correctly."""
    mock_config_entry.add_to_hass(hass)

    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

    from custom_components.mercury_switch import MercurySwitchData
    from custom_components.mercury_switch.mercury_switch import (
        HomeAssistantMercurySwitch,
    )

    switch = HomeAssistantMercurySwitch(hass, mock_config_entry)
    switch.api = mock_mercury_switch_api
    switch.model = "SG108Pro"

    coordinator = DataUpdateCoordinator(
        hass,
        None,
        name="test",
        update_method=AsyncMock(return_value=mock_switch_infos),
        config_entry=mock_config_entry,
    )
    coordinator.data = mock_switch_infos

    mock_config_entry.runtime_data = MercurySwitchData(switch, coordinator)

    async_add_entities = AsyncMock()
    await async_setup_entry(hass, mock_config_entry, async_add_entities)

    # Verify entities were added
    assert async_add_entities.called
    entities = async_add_entities.call_args[0][0]

    # Should have 8 port status binary sensors
    assert len(entities) == 8

    # Check entity keys
    entity_keys = [entity.entity_description.key for entity in entities]
    for port_num in range(1, 9):
        assert f"port_{port_num}_status" in entity_keys

    # Check device class
    for entity in entities:
        assert (
            entity.entity_description.device_class
            == BinarySensorDeviceClass.CONNECTIVITY
        )


async def test_binary_sensor_values(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_mercury_switch_api,
    mock_switch_infos,
) -> None:
    """Test that binary sensor entities have correct values."""
    mock_config_entry.add_to_hass(hass)

    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

    from custom_components.mercury_switch import MercurySwitchData
    from custom_components.mercury_switch.mercury_switch import (
        HomeAssistantMercurySwitch,
    )

    switch = HomeAssistantMercurySwitch(hass, mock_config_entry)
    switch.api = mock_mercury_switch_api
    switch.model = "SG108Pro"

    coordinator = DataUpdateCoordinator(
        hass,
        None,
        name="test",
        update_method=AsyncMock(return_value=mock_switch_infos),
        config_entry=mock_config_entry,
    )
    coordinator.data = mock_switch_infos

    mock_config_entry.runtime_data = MercurySwitchData(switch, coordinator)

    async_add_entities = AsyncMock()
    await async_setup_entry(hass, mock_config_entry, async_add_entities)

    entities = async_add_entities.call_args[0][0]

    # Find port 1 entity (should be on)
    port_1_entity = next(
        (e for e in entities if e.entity_description.key == "port_1_status"), None
    )
    assert port_1_entity is not None
    port_1_entity.async_update_device()
    assert port_1_entity.is_on is True

    # Find port 2 entity (should be off)
    port_2_entity = next(
        (e for e in entities if e.entity_description.key == "port_2_status"), None
    )
    assert port_2_entity is not None
    port_2_entity.async_update_device()
    assert port_2_entity.is_on is False

    # Find port 4 entity (should be on)
    port_4_entity = next(
        (e for e in entities if e.entity_description.key == "port_4_status"), None
    )
    assert port_4_entity is not None
    port_4_entity.async_update_device()
    assert port_4_entity.is_on is True
