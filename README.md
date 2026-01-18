# Home Assistant Mercury Switch Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/daxingplay/home-assistant-mercury-switch.svg)](https://github.com/daxingplay/home-assistant-mercury-switch/releases)

Home Assistant integration for Mercury network switches. This integration provides sensors and binary sensors to monitor port status, traffic statistics, VLAN configuration, and system information from your Mercury switch.

## Features

- **Port Monitoring**: Real-time status and connection speed for each port
- **Traffic Statistics**: TX/RX packet counts for each port
- **VLAN Support**: Monitor 802.1Q VLAN configuration, including VLAN names, tagged/untagged ports
- **System Information**: Switch model, MAC address, IP address, firmware version
- **Auto-Detection**: Automatically detects supported Mercury switch models
- **Config Flow**: Easy setup through Home Assistant UI

## Supported Models

Currently tested and supported:
- **SG108Pro** (8 ports)

More models can be added - see [Contributing](#contributing) below.

## Installation

### Option 1: HACS (Recommended)

1. In your Home Assistant instance, go to **HACS** (Search: ">hacs")
2. Click on the right corner on the vertical dots and select "Custom Repositories"
3. Add this repository URL: `https://github.com/daxingplay/home-assistant-mercury-switch`
4. Select category: **Integration**
5. Click "Add"
6. Click "Install" on the repository card
7. Restart Home Assistant

### Option 2: Manual Installation

1. Download the latest release from [Releases](https://github.com/daxingplay/home-assistant-mercury-switch/releases)
2. Extract the `custom_components` folder to your Home Assistant configuration directory
3. Restart Home Assistant

## Configuration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Mercury Switch**
4. Enter your switch details:
   - **Host**: IP address of your Mercury switch (e.g., `192.168.1.100`)
   - **Username**: Switch admin username (default: `admin`)
   - **Password**: Switch admin password
5. Click **Submit**

The integration will automatically detect your switch model and create entities.

## Entities

### Device Sensors

- **IP Address**: Switch IP address
- **Model**: Switch model name
- **MAC Address**: Switch MAC address
- **Firmware**: Firmware version
- **Hardware**: Hardware version
- **VLAN Type**: Active VLAN type (802.1Q, Port-based, MTU, or None)
- **VLAN Count**: Number of configured VLANs

### Port Sensors (per port)

- **Port {N} Speed**: Configured port speed
- **Port {N} Link Speed**: Actual connection speed
- **Port {N} TX Packets**: Total transmitted packets
- **Port {N} RX Packets**: Total received packets

### Port Binary Sensors (per port)

- **Port {N} Status**: Port connectivity status (on/off)

### VLAN Sensors (if 802.1Q VLAN is enabled)

For each VLAN:
- **VLAN {ID} Name**: VLAN name
- **VLAN {ID} Tagged Ports**: List of tagged ports
- **VLAN {ID} Untagged Ports**: List of untagged ports

## Requirements

- Home Assistant 2024.1.0 or later
- HACS 2.0.5 or later (if using HACS)
- `py-mercury-switch-api>=0.3.0` (automatically installed)

## Troubleshooting

### Integration won't load

- Verify the switch is accessible from your Home Assistant instance
- Check that the IP address, username, and password are correct
- Review Home Assistant logs for error messages

### No entities created

- Ensure the switch is powered on and connected to the network
- Check that the integration successfully connected during setup
- Verify your switch model is supported

### Port status shows as "off" when cable is connected

- Some switches may require a device to be connected to detect link status
- Check the switch's web interface to verify port status

## Contributing

Contributions are welcome! If you have a Mercury switch model that isn't currently supported:

1. Check if the API package (`py-mercury-switch-api`) supports your model
2. If not, contribute model support to the API package first
3. Test the integration with your switch model
4. Submit a pull request or open an issue

## API Package

This integration uses the [`py-mercury-switch-api`](https://pypi.org/project/py-mercury-switch-api/) Python package for communication with Mercury switches. The API package is designed to support multiple Mercury switch models.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Credits

- Inspired by the [NETGEAR Plus integration](https://github.com/ckarrie/ha-netgear-plus)
- Built using the [Home Assistant Integration Blueprint](https://github.com/home-assistant/integration_blueprint)

## Support

- [GitHub Issues](https://github.com/daxingplay/home-assistant-mercury-switch/issues)
- [Home Assistant Community Forum](https://community.home-assistant.io/)
