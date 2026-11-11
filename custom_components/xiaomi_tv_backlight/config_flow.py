"""Config flow for Xiaomi TV Backlight Control."""
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import BacklightApi
from .const import DOMAIN

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self.host = ""
        self.info = {}

    async def async_step_zeroconf(self, discovery_info):
        host = discovery_info.host
        self.host = f"http://[{host}]:{discovery_info.port}" if ":" in host else f"http://{host}:{discovery_info.port}"
        try:
            self.info = await BacklightApi(async_get_clientsession(self.hass), self.host).info()
        except (aiohttp.ClientError, TimeoutError, ValueError):
            return self.async_abort(reason="cannot_connect")
        await self.async_set_unique_id(self.info["id"])
        self._abort_if_unique_id_configured(updates={"host": self.host})
        self.context["title_placeholders"] = {"name": self.info.get("model", "Xiaomi TV")}
        return await self.async_step_pair()

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            try:
                api = BacklightApi(async_get_clientsession(self.hass), user_input["host"])
                self.host = api.base
                self.info = await api.info()
            except (aiohttp.ClientError, TimeoutError, ValueError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(self.info["id"])
                self._abort_if_unique_id_configured(updates={"host": self.host})
                return await self.async_step_pair()
        return self.async_show_form(step_id="user", data_schema=vol.Schema({vol.Required("host"): str}), errors=errors)

    async def async_step_pair(self, user_input=None):
        errors = {}
        if user_input:
            code = user_input["code"].strip()
            if len(code) != 6 or not code.isascii() or not code.isdigit():
                errors["base"] = "invalid_code"
            else:
                try:
                    api = BacklightApi(async_get_clientsession(self.hass), self.host)
                    token = await api.pair(code)
                    api.token = token
                    await api.read()
                except aiohttp.ClientResponseError as error:
                    errors["base"] = "invalid_code" if error.status == 403 else "cannot_connect"
                except (aiohttp.ClientError, TimeoutError, ValueError):
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(title=self.info.get("model", "Xiaomi TV"),
                        data={"host": self.host, "token": token, "model": self.info.get("model", "Xiaomi TV")})
        return self.async_show_form(step_id="pair", data_schema=vol.Schema({vol.Required("code"): str}), errors=errors)
