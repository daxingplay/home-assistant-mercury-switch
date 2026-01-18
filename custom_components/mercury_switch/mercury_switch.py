"""HomeAssistant Setup for Mercury Switch API."""

from __future__ import annotations

import asyncio
import logging
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from py_mercury_switch_api import MercurySwitchConnector
from py_mercury_switch_api import __version__ as api_version

from .const import DOMAIN
from .errors import CannotLoginError

_LOGGER = logging.getLogger(__name__)


def get_api(host: str, username: str, password: str) -> MercurySwitchConnector:
    """Get the Mercury Switch API and login to it."""
    api: MercurySwitchConnector = MercurySwitchConnector(host, username, password)
    try:
        api.autodetect_model()
    except Exception as e:
        _LOGGER.warning("Could not autodetect model: %s", e)
    _LOGGER.info(
        "Created MercurySwitchConnector API version %s for model %s.",
        str(api_version),
        str(api.switch_model.MODEL_NAME),
    )
    # Login to verify credentials
    if not api.get_login_cookie():
        raise CannotLoginError
    return api


class HomeAssistantMercurySwitch:
    """Class to manage the Mercury switch integration with Home Assistant."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the HomeAssistantMercurySwitch class."""
        if not entry.unique_id:
            error_message = "ConfigEntry must have a unique_id"
            raise ValueError(error_message)
        self.hass = hass
        self.entry = entry
        self.entry_id = entry.entry_id
        self.unique_id = entry.unique_id
        self.device_name = entry.title
        self._host: str = entry.data[CONF_HOST]
        self._username = entry.data[CONF_USERNAME]
        self._password = entry.data[CONF_PASSWORD]

        # set on setup
        self.api: Optional[MercurySwitchConnector] = None
        self.model = None

        # async lock
        self.api_lock = asyncio.Lock()

    def _setup(self) -> bool:
        """Set up the Mercury switch."""
        self.api = get_api(host=self._host, username=self._username, password=self._password)
        if not self.api.switch_model or self.api.switch_model.MODEL_NAME == "":
            _LOGGER.info(
                "[HomeAssistantMercurySwitch._setup] "
                "No MercurySwitchConnector switch_model set, "
                "autodetecting model via MercurySwitchConnector.autodetect_model()"
            )
            try:
                self.api.autodetect_model()
            except Exception as e:
                _LOGGER.warning("Could not autodetect model: %s", e)
            _LOGGER.info(
                "[HomeAssistantMercurySwitch._setup] Autodetected model: %s",
                str(self.api.switch_model.MODEL_NAME),
            )
        self.model = self.api.switch_model.MODEL_NAME
        return True

    async def async_setup(self) -> bool:
        """Set up the Mercury switch asynchronously."""
        async with self.api_lock:
            if not await self.hass.async_add_executor_job(self._setup):
                return False
        return True

    async def async_get_switch_infos(self) -> Optional[dict[str, Any]]:
        """Get switch information asynchronously."""
        async with self.api_lock:
            return await self.hass.async_add_executor_job(self.api.get_switch_infos)  # type: ignore[attr-defined]


class MercurySwitchCoordinatorEntity(CoordinatorEntity):
    """Base class for a Mercury switch entity."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, switch: HomeAssistantMercurySwitch
    ) -> None:
        """Initialize a Mercury device."""
        super().__init__(coordinator)
        self._switch = switch
        self._name = switch.device_name
        self._unique_id = switch.unique_id

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        super()._handle_coordinator_update()

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self) -> str:
        """Return the name."""
        return self._name

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._switch.unique_id)},
        )


class MercurySwitchAPICoordinatorEntity(MercurySwitchCoordinatorEntity):
    """Base class for a Mercury switch entity."""

    def __init__(
        self, coordinator: DataUpdateCoordinator, switch: HomeAssistantMercurySwitch
    ) -> None:
        """Initialize a Mercury device."""
        super().__init__(coordinator, switch)

    @abstractmethod
    @callback
    def async_update_device(self) -> None:
        """Update the Mercury device."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_update_device()
        super()._handle_coordinator_update()
