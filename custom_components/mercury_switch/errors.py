"""Errors for the Mercury Switch integration."""

from homeassistant.exceptions import HomeAssistantError


class CannotLoginError(HomeAssistantError):
    """Unable to login to the switch."""
