"""Poll local backlight state, retaining the requested offline-zero display."""
import logging
from datetime import timedelta
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN

class BacklightCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, api):
        super().__init__(hass, logging.getLogger(__name__), name=DOMAIN,
            config_entry=entry, update_interval=timedelta(seconds=15))
        self.api = api

    async def _async_update_data(self):
        try:
            return {"level": await self.api.read(), "online": True}
        except (aiohttp.ClientError, TimeoutError, ValueError):
            return {"level": 0, "online": False}
