"""Pytest fixtures for Mercury Switch integration tests."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.mercury_switch.const import DOMAIN


@pytest.fixture
def mock_mercury_switch_api():
    """Create a mocked MercurySwitchConnector."""
    with patch("custom_components.mercury_switch.mercury_switch.MercurySwitchConnector") as mock:
        connector = MagicMock()
        connector.get_login_cookie = MagicMock(return_value=True)
        connector.autodetect_model = MagicMock()
        connector.get_unique_id = MagicMock(return_value="sg108pro_192_168_1_100")
        connector.get_switch_infos = MagicMock(
            return_value={
                "switch_model": "SG108-Pro",
                "switch_mac": "00:AA:BB:CC:DD:EE",
                "switch_ip": "192.168.1.100",
                "switch_firmware": "1.0.0 Build 20180515 Rel.60767",
                "switch_hardware": "SG108 Pro 1.0",
                "port_1_status": "on",
                "port_1_connection_speed": "1000M全双工",
                "port_1_tx_good": 1000,
                "port_1_rx_good": 2000,
                "port_2_status": "off",
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
            }
        )
        connector.ports = 8
        connector.switch_model = MagicMock()
        connector.switch_model.MODEL_NAME = "SG108Pro"
        mock.return_value = connector
        yield connector


@pytest.fixture
def mock_mercury_switch_api_auth_fail():
    """Create a mocked connector that fails authentication."""
    with patch("custom_components.mercury_switch.mercury_switch.MercurySwitchConnector") as mock:
        connector = MagicMock()
        connector.get_login_cookie = MagicMock(return_value=False)
        connector.autodetect_model = MagicMock()
        mock.return_value = connector
        yield connector


@pytest.fixture
def mock_mercury_switch_api_connection_error():
    """Create a mocked connector that raises connection error."""
    with patch("custom_components.mercury_switch.mercury_switch.MercurySwitchConnector") as mock:
        from py_mercury_switch_api.exceptions import MercurySwitchConnectionError

        mock.side_effect = MercurySwitchConnectionError("Connection failed")
        yield mock
