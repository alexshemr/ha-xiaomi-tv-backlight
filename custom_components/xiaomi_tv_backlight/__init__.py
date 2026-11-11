"""Xiaomi TV Backlight Control integration."""
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import BacklightApi
from .coordinator import BacklightCoordinator

PLATFORMS = [Platform.NUMBER, Platform.BINARY_SENSOR]

async def async_setup_entry(hass, entry):
    api = BacklightApi(async_get_clientsession(hass), entry.data["host"], entry.data["token"])
    coordinator = BacklightCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(async_reload))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_reload(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
