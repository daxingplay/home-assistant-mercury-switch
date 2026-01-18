"""Sensors for Mercury Switch."""

from __future__ import annotations

import logging
from collections import OrderedDict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfInformation
from homeassistant.core import callback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import MercurySwitchConfigEntry
from .mercury_entities import (
    MercurySwitchAPICoordinatorEntity,
    MercurySwitchSensorEntityDescription,
    MercurySwitchRouterSensorEntity,
)
from .mercury_switch import HomeAssistantMercurySwitch

_LOGGER = logging.getLogger(__name__)


DEVICE_SENSOR_TYPES = [
    MercurySwitchSensorEntityDescription(
        key="switch_firmware",
        name="Firmware",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=None,
        device_class=None,
        icon="mdi:text",
    ),
    MercurySwitchSensorEntityDescription(
        key="switch_hardware",
        name="Hardware",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=None,
        device_class=None,
        icon="mdi:text",
    ),
    MercurySwitchSensorEntityDescription(
        key="switch_mac",
        name="MAC Address",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=None,
        device_class=None,
        icon="mdi:network",
    ),
    MercurySwitchSensorEntityDescription(
        key="switch_ip",
        name="IP Address",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=None,
        device_class=None,
        icon="mdi:ip-network",
    ),
]

PORT_TEMPLATE = OrderedDict(
    {
        "port_{port}_speed": {
            "name": "Port {port} Speed",
            "native_unit_of_measurement": None,
            "device_class": None,
            "icon": "mdi:speedometer",
        },
        "port_{port}_tx_good": {
            "name": "Port {port} TX Packets",
            "native_unit_of_measurement": "packets",
            "device_class": None,
            "state_class": SensorStateClass.TOTAL_INCREASING,
            "icon": "mdi:upload",
        },
        "port_{port}_rx_good": {
            "name": "Port {port} RX Packets",
            "native_unit_of_measurement": "packets",
            "device_class": None,
            "state_class": SensorStateClass.TOTAL_INCREASING,
            "icon": "mdi:download",
        },
    }
)

VLAN_TEMPLATE = OrderedDict(
    {
        "vlan_{vlan_id}_name": {
            "name": "VLAN {vlan_id} Name",
            "native_unit_of_measurement": None,
            "device_class": None,
            "icon": "mdi:tag",
        },
        "vlan_{vlan_id}_tagged_ports": {
            "name": "VLAN {vlan_id} Tagged Ports",
            "native_unit_of_measurement": None,
            "device_class": None,
            "icon": "mdi:tag-multiple",
        },
        "vlan_{vlan_id}_untagged_ports": {
            "name": "VLAN {vlan_id} Untagged Ports",
            "native_unit_of_measurement": None,
            "device_class": None,
            "icon": "mdi:tag-outline",
        },
    }
)

VLAN_GLOBAL_SENSORS = OrderedDict(
    {
        "vlan_type": {
            "name": "VLAN Type",
            "native_unit_of_measurement": None,
            "device_class": None,
            "icon": "mdi:tag",
        },
        "vlan_enabled": {
            "name": "802.1Q VLAN Enabled",
            "native_unit_of_measurement": None,
            "device_class": None,
            "icon": "mdi:tag",
        },
        "vlan_count": {
            "name": "VLAN Count",
            "native_unit_of_measurement": None,
            "device_class": None,
            "icon": "mdi:tag-multiple",
        },
    }
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MercurySwitchConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for Mercury Switch component."""
    del hass
    switch = entry.runtime_data.switch
    coordinator_switch_infos = entry.runtime_data.coordinator_switch_infos

    # Device entities
    switch_entities = []

    for description in DEVICE_SENSOR_TYPES:
        descr_entity = MercurySwitchRouterSensorEntity(
            coordinator=coordinator_switch_infos,
            switch=switch,
            entity_description=description,
        )
        switch_entities.append(descr_entity)

    if switch.api is None:
        _LOGGER.error("switch.api is None, cannot proceed with setting up sensors.")
        return

    ports_cnt = getattr(switch.api, "ports", 0)
    _LOGGER.info(
        "[sensor.async_setup_entry] setting up Platform.SENSOR for %d Switch Ports",
        ports_cnt,
    )

    # Port sensors
    for i in range(ports_cnt):
        port_nr = i + 1
        for port_sensor_key, port_sensor_data in PORT_TEMPLATE.items():
            description = MercurySwitchSensorEntityDescription(
                key=port_sensor_key.format(port=port_nr),
                name=port_sensor_data["name"].format(port=port_nr),
                native_unit_of_measurement=port_sensor_data.get("native_unit_of_measurement"),
                device_class=port_sensor_data.get("device_class"),
                state_class=port_sensor_data.get("state_class"),
                icon=port_sensor_data.get("icon"),
            )
            port_sensor_entity = MercurySwitchRouterSensorEntity(
                coordinator=coordinator_switch_infos,
                switch=switch,
                entity_description=description,
            )
            switch_entities.append(port_sensor_entity)

    # VLAN global sensors
    for vlan_sensor_key, vlan_sensor_data in VLAN_GLOBAL_SENSORS.items():
        description = MercurySwitchSensorEntityDescription(
            key=vlan_sensor_key,
            name=vlan_sensor_data["name"],
            native_unit_of_measurement=vlan_sensor_data.get("native_unit_of_measurement"),
            device_class=vlan_sensor_data.get("device_class"),
            icon=vlan_sensor_data.get("icon"),
        )
        vlan_sensor_entity = MercurySwitchRouterSensorEntity(
            coordinator=coordinator_switch_infos,
            switch=switch,
            entity_description=description,
        )
        switch_entities.append(vlan_sensor_entity)

    # VLAN per-VLAN sensors (dynamically created based on discovered VLANs)
    if coordinator_switch_infos.data:
        vlan_count = coordinator_switch_infos.data.get("vlan_count", 0)
        if vlan_count > 0:
            # Find all VLAN IDs from the data
            vlan_ids = []
            for key in coordinator_switch_infos.data.keys():
                if key.startswith("vlan_") and key.endswith("_name"):
                    try:
                        vlan_id = int(key.replace("vlan_", "").replace("_name", ""))
                        vlan_ids.append(vlan_id)
                    except ValueError:
                        continue

            for vlan_id in vlan_ids:
                for vlan_sensor_key, vlan_sensor_data in VLAN_TEMPLATE.items():
                    description = MercurySwitchSensorEntityDescription(
                        key=vlan_sensor_key.format(vlan_id=vlan_id),
                        name=vlan_sensor_data["name"].format(vlan_id=vlan_id),
                        native_unit_of_measurement=vlan_sensor_data.get("native_unit_of_measurement"),
                        device_class=vlan_sensor_data.get("device_class"),
                        icon=vlan_sensor_data.get("icon"),
                    )
                    vlan_sensor_entity = MercurySwitchRouterSensorEntity(
                        coordinator=coordinator_switch_infos,
                        switch=switch,
                        entity_description=description,
                    )
                    switch_entities.append(vlan_sensor_entity)

    async_add_entities(switch_entities)
