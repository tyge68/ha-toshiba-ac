"""Sensor platform for Toshiba AC integration."""
from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID, CONF_NAME, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from .const import CONF_CLIMATE_ID
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize Toshiba AC config entry."""
    # registry = er.async_get(hass)
    # Validate + resolve entity registry id to entity_id
    # entity_id = er.async_validate_entity_id(
    #    registry, config_entry.options[CONF_ENTITY_ID]
    # )
    # TODO Optionally validate config entry options before creating entity


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the climate platform."""
    device_id = config[CONF_ID]
    climate_id = config[CONF_CLIMATE_ID]
    add_entities(
        [
            ToshibaSensorEntity(hass, "temperature", device_id, climate_id),
            ToshibaSensorEntity(hass, "humidity", device_id, climate_id),
        ],
        True,
    )


class ToshibaSensorEntity(SensorEntity):
    """Toshiba Sensor."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, hass, device_type, device_id, climate_id) -> None:
        super().__init__()
        self._device_id = device_id
        self._hass = hass
        self._climate_id = climate_id
        self._type = device_type
        self._attr_name = device_type
        if "temperature" in device_type:
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
        else:
            self._attr_native_unit_of_measurement = "%"
            self._attr_device_class = SensorDeviceClass.HUMIDITY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._attr_name

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self._device_id + "_" + self._type

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        entity_state = self._hass.states.get(self._climate_id)
        if entity_state is not None:
            self._attr_native_value = entity_state.attributes.get(
                "current_" + self._type
            )
