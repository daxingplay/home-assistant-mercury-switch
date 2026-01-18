"""Test sensor entities for Mercury Switch integration."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.components.sensor import SensorStateClass
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.mercury_switch.const import DOMAIN
from custom_components.mercury_switch.sensor import async_setup_entry


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
        "switch_model": "SG108-Pro",
        "switch_mac": "00:AA:BB:CC:DD:EE",
        "switch_ip": "192.168.1.100",
        "switch_firmware": "1.0.0 Build 20180515 Rel.60767",
        "switch_hardware": "SG108 Pro 1.0",
        "port_1_status": "on",
        "port_1_speed": "1000M全双工",
        "port_1_connection_speed": "1000M全双工",
        "port_1_tx_good": 1000,
        "port_1_rx_good": 2000,
        "port_2_status": "off",
        "port_2_speed": "断开",
        "port_2_connection_speed": "断开",
        "port_2_tx_good": 0,
        "port_2_rx_good": 0,
        "vlan_enabled": True,
        "vlan_type": "802.1Q",
        "vlan_count": 7,
        "vlan_1_name": "Default",
        "vlan_10_name": "VLAN10",
        "vlan_10_tagged_ports": "1, 7",
        "vlan_10_untagged_ports": "",
        "vlan_20_name": "VLAN20",
        "vlan_20_tagged_ports": "",
        "vlan_20_untagged_ports": "2",
    }


async def test_sensor_entities_created(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_mercury_switch_api,
    mock_switch_infos,
) -> None:
    """Test that sensor entities are created correctly."""
    mock_config_entry.add_to_hass(hass)

    # Create runtime data
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

    # Setup sensors
    async_add_entities = AsyncMock()
    await async_setup_entry(hass, mock_config_entry, async_add_entities)

    # Verify entities were added
    assert async_add_entities.called
    entities = async_add_entities.call_args[0][0]

    # Check that we have device sensors, port sensors, and VLAN sensors
    assert len(entities) > 0

    # Check for device info sensors
    entity_keys = [entity.entity_description.key for entity in entities]
    assert "switch_firmware" in entity_keys
    assert "switch_hardware" in entity_keys
    assert "switch_mac" in entity_keys
    assert "switch_ip" in entity_keys

    # Check for port sensors
    assert "port_1_speed" in entity_keys
    assert "port_1_tx_good" in entity_keys
    assert "port_1_rx_good" in entity_keys

    # Check for VLAN sensors
    assert "vlan_type" in entity_keys
    assert "vlan_enabled" in entity_keys
    assert "vlan_count" in entity_keys
    assert "vlan_10_name" in entity_keys


async def test_sensor_values(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_mercury_switch_api,
    mock_switch_infos,
) -> None:
    """Test that sensor entities have correct values."""
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

    # Find specific entities and check their values
    firmware_entity = next(
        (e for e in entities if e.entity_description.key == "switch_firmware"), None
    )
    assert firmware_entity is not None
    firmware_entity.async_update_device()
    assert firmware_entity.native_value == "1.0.0 Build 20180515 Rel.60767"

    port_tx_entity = next(
        (e for e in entities if e.entity_description.key == "port_1_tx_good"), None
    )
    assert port_tx_entity is not None
    port_tx_entity.async_update_device()
    assert port_tx_entity.native_value == 1000
    assert (
        port_tx_entity.entity_description.state_class
        == SensorStateClass.TOTAL_INCREASING
    )

    vlan_count_entity = next(
        (e for e in entities if e.entity_description.key == "vlan_count"), None
    )
    assert vlan_count_entity is not None
    vlan_count_entity.async_update_device()
    assert vlan_count_entity.native_value == 7
