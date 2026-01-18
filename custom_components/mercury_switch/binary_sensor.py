"""Binary Sensors for Mercury Switch."""

from __future__ import annotations

import logging
from collections import OrderedDict
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import BinarySensorDeviceClass

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import MercurySwitchConfigEntry
from .mercury_entities import (
    MercurySwitchBinarySensorEntityDescription,
    MercurySwitchRouterBinarySensorEntity,
)

_LOGGER = logging.getLogger(__name__)

PORT_TEMPLATE = OrderedDict(
    {
        "port_{port}_status": {
            "name": "Port {port} Status",
            "device_class": BinarySensorDeviceClass.CONNECTIVITY,
        },
    }
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MercurySwitchConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors for Mercury Switch component."""
    del hass
    switch = entry.runtime_data.switch
    coordinator_switch_infos = entry.runtime_data.coordinator_switch_infos

    # Router entities
    switch_entities = []

    ports_cnt = getattr(switch.api, "ports", 0) if switch.api is not None else 0
    _LOGGER.info(
        "[binary_sensor.async_setup_entry] "
        "setting up Platform.BINARY_SENSOR for %d Switch Ports",
        ports_cnt,
    )
    for i in range(ports_cnt):
        port_nr = i + 1
        for port_sensor_key, port_sensor_data in PORT_TEMPLATE.items():
            description = MercurySwitchBinarySensorEntityDescription(
                key=port_sensor_key.format(port=port_nr),
                name=port_sensor_data["name"].format(port=port_nr),
                device_class=port_sensor_data["device_class"],
                icon=port_sensor_data.get("icon"),
            )
            port_status_binarysensor_entity = MercurySwitchRouterBinarySensorEntity(
                coordinator=coordinator_switch_infos,
                switch=switch,
                entity_description=description,
            )
            switch_entities.append(port_status_binarysensor_entity)

    async_add_entities(switch_entities)
