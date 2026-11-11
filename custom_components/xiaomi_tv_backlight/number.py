"""Backlight number entity."""
import aiohttp
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([BacklightNumber(entry)])

class BacklightNumber(CoordinatorEntity, NumberEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "backlight"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:brightness-6"

    def __init__(self, entry):
        super().__init__(entry.runtime_data)
        self._attr_unique_id = f"{entry.unique_id}_backlight"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.unique_id)},
            name=entry.title, manufacturer="Xiaomi", model=entry.data["model"])

    @property
    def native_value(self):
        return self.coordinator.data["level"]

    async def async_set_native_value(self, value):
        if value != int(value) or not 0 <= value <= 100:
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key="invalid_level")
        try:
            level = await self.coordinator.api.write(int(value))
        except (aiohttp.ClientError, TimeoutError, ValueError) as error:
            await self.coordinator.async_request_refresh()
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key="cannot_connect") from error
        self.coordinator.async_set_updated_data({"level": level, "online": True})
