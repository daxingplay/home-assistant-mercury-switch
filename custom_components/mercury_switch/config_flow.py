"""Config flow to configure the Mercury Switch integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback

from .const import DOMAIN
from .errors import CannotLoginError
from .mercury_switch import get_api

_LOGGER = logging.getLogger(__name__)


def _user_schema_with_defaults(user_input: dict[str, Any]) -> vol.Schema:
    """Return schema with defaults."""
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=user_input.get(CONF_HOST, "")): str,
            vol.Required(
                CONF_USERNAME, default=user_input.get(CONF_USERNAME, "admin")
            ): str,
            vol.Required(CONF_PASSWORD, default=user_input.get(CONF_PASSWORD, "")): str,
        }
    )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options for the component."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init", data_schema=vol.Schema({}))


class MercurySwitchFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the mercury switch config flow."""
        self.placeholders = {
            CONF_HOST: "192.168.1.1",
        }

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,  # noqa: ARG004
    ) -> OptionsFlowHandler:
        """Get the options flow."""
        return OptionsFlowHandler()

    async def _show_setup_form(
        self,
        user_input: dict[str, Any] | None = None,
        errors: dict[str, str] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Show the setup form to the user."""
        if not user_input:
            user_input = {}

        data_schema = _user_schema_with_defaults(user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors or {},
            description_placeholders=self.placeholders,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is None:
            return await self._show_setup_form()

        host = user_input[CONF_HOST]
        username = user_input[CONF_USERNAME]
        password = user_input[CONF_PASSWORD]

        # Open connection and check authentication
        try:
            api = await self.hass.async_add_executor_job(
                get_api, host, username, password
            )
        except CannotLoginError:
            errors["base"] = "invalid_auth"
        except (ConnectionError, TimeoutError, OSError):
            _LOGGER.exception("Error connecting to switch")
            errors["base"] = "cannot_connect"

        if errors:
            return await self._show_setup_form(user_input, errors)

        config_data = {
            CONF_HOST: host,
            CONF_USERNAME: username,
            CONF_PASSWORD: password,
        }

        # Check if already configured
        unique_id = await self.hass.async_add_executor_job(api.get_unique_id)
        await self.async_set_unique_id(unique_id, raise_on_progress=False)
        self._abort_if_unique_id_configured(updates=config_data)

        # set autodetected switch model name
        model_name = api.switch_model.MODEL_NAME
        name = f"{model_name} ({host})"

        return self.async_create_entry(
            title=name,
            data=config_data,
        )
