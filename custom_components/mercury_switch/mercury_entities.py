"""Entity definitions for Mercury Switches."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import (
    RestoreSensor,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.core import callback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .mercury_switch import (
    HomeAssistantMercurySwitch,
    MercurySwitchAPICoordinatorEntity,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class MercurySwitchSensorEntityDescription(SensorEntityDescription):
    """Describes Mercury Switch sensor entities."""

    value: Callable = lambda data: data
    index: int = 0


@dataclass(frozen=True)
class MercurySwitchBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Mercury Switch binary sensor entities."""

    value: Callable = lambda data: data
    index: int = 0

    device_class: BinarySensorDeviceClass | str | None = None
    last_reset: datetime | None = None
    native_unit_of_measurement: str | None = None
    options: list[str] | None = None
    state_class: SensorStateClass | str | None = None
    suggested_display_precision: int | None = None
    suggested_unit_of_measurement: str | None = None
    unit_of_measurement: None = None  # Type override, use native_unit_of_measurement
    native_precision = None


class MercurySwitchRouterSensorEntity(MercurySwitchAPICoordinatorEntity, RestoreSensor):
    """Representation of a sensor on a Mercury switch."""

    entity_description: MercurySwitchSensorEntityDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        switch: HomeAssistantMercurySwitch,
        entity_description: MercurySwitchSensorEntityDescription,
    ) -> None:
        """Initialize a Mercury device."""
        super().__init__(coordinator, switch)
        self.entity_description = entity_description
        self._name = f"{switch.device_name} {entity_description.name}"
        self._unique_id = (
            f"{switch.unique_id}-{entity_description.key}-{entity_description.index}"
        )
        self._value: StateType | date | datetime | Decimal = None
        self.async_update_device()

    def __repr__(self) -> str:
        """Return human readable object representation."""
        return f"<MercurySwitchRouterSensorEntity unique_id={self._unique_id}>"

    @property
    def name(self) -> str:
        """Return the name."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return the state of the sensor."""
        return self._value

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if self.coordinator.data is None:
            sensor_data = await self.async_get_last_sensor_data()
            if sensor_data is not None:
                self._value = sensor_data.native_value

    @callback
    def async_update_device(self) -> None:
        """Update the Mercury device."""
        if self.coordinator.data is None:
            return

        data = self.coordinator.data.get(self.entity_description.key)
        if data is None:
            self._value = None
            _LOGGER.debug(
                "key '%s' not in Mercury switch response '%s'",
                self.entity_description.key,
                data,
            )
            return

        self._value = self.entity_description.value(data)


class MercurySwitchRouterBinarySensorEntity(
    MercurySwitchAPICoordinatorEntity, BinarySensorEntity
):
    """Representation of a binary sensor on a Mercury switch."""

    entity_description: MercurySwitchBinarySensorEntityDescription
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        switch: HomeAssistantMercurySwitch,
        entity_description: MercurySwitchBinarySensorEntityDescription,
    ) -> None:
        """Initialize a Mercury device."""
        super().__init__(coordinator, switch)
        self.entity_description = entity_description
        self._name = f"{switch.device_name} {entity_description.name}"
        self._unique_id = (
            f"{switch.unique_id}-{entity_description.key}-{entity_description.index}"
        )
        self._value = False
        self.async_update_device()

    def __repr__(self) -> str:
        """Return human readable object representation."""
        return f"<MercurySwitchRouterBinarySensorEntity unique_id={self._unique_id}>"

    @property
    def name(self) -> str:
        """Return the name."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def is_on(self) -> bool:
        """Return the state of the binary sensor."""
        return self._value

    @callback
    def async_update_device(self) -> None:
        """Update the Mercury device."""
        if self.coordinator.data is None:
            return

        data = self.coordinator.data.get(self.entity_description.key)
        if data is None:
            self._value = False
            _LOGGER.debug(
                "key '%s' not in Mercury switch response '%s'",
                self.entity_description.key,
                data,
            )
            return

        # Convert to boolean
        if isinstance(data, str):
            self._value = data.lower() in ["on", "true", "1", "yes"]
        elif isinstance(data, bool):
            self._value = data
        elif isinstance(data, (int, float)):
            self._value = bool(data)
        else:
            self._value = bool(data)
