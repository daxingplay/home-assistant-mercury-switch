"""HomeAssistant integration for Mercury Switches."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

from homeassistant.const import CONF_HOST
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, PLATFORMS, SCAN_INTERVAL
from .errors import CannotLoginError
from .mercury_switch import HomeAssistantMercurySwitch

_LOGGER = logging.getLogger(__name__)

type MercurySwitchConfigEntry = ConfigEntry[MercurySwitchData]


@dataclass
class MercurySwitchData:
    """Runtime Data for ConfigEntry."""

    switch: HomeAssistantMercurySwitch
    coordinator_switch_infos: DataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: MercurySwitchConfigEntry
) -> bool:
    """Set up Mercury Switch component."""
    switch = HomeAssistantMercurySwitch(hass, entry)
    try:
        if not await switch.async_setup():
            raise ConfigEntryNotReady
    except CannotLoginError as ex:
        raise ConfigEntryNotReady from ex

    entry.async_on_unload(entry.add_update_listener(update_listener))

    if not entry.unique_id:
        message = "entry.unique_id not defined."
        raise NameError(message)
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.unique_id)},
        manufacturer="Mercury",
        name=switch.device_name,
        model=switch.model,
        configuration_url=f"http://{entry.data[CONF_HOST]}/",
    )

    async def async_update_switch_infos() -> dict[str, Any] | None:
        """Fetch data from the switch."""
        return await switch.async_get_switch_infos()

    # Create update coordinators
    coordinator_switch_infos = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{switch.device_name} Switch infos",
        update_method=async_update_switch_infos,
        update_interval=SCAN_INTERVAL,
        config_entry=entry,
    )

    await coordinator_switch_infos.async_config_entry_first_refresh()

    entry.runtime_data = MercurySwitchData(switch, coordinator_switch_infos)  # type: ignore[assignment]

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)
