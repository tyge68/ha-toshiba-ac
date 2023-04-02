"""Climate platform for Toshiba AC integration."""
from __future__ import annotations
import functools as ft
from homeassistant.components.climate import (
    ClimateEntity,
    HVACMode,
    ClimateEntityFeature,
    ATTR_HVAC_MODE,
    FAN_AUTO,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
    PRESET_NONE,
    PRESET_ECO,
    PRESET_BOOST,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID, CONF_NAME, UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from .const import CONF_IP, CONF_LOCAL_KEY, DOMAIN
from toshiba_ac import (
    IRCodeGenerator,
    UnitType,
    FanType,
    ModeType,
    SpecialModeType,
)

# from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from tinytuya import Contrib
import logging
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)


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
    name = config[CONF_NAME]
    device_id = config[CONF_ID]
    ip = config[CONF_IP]
    localkey = config[CONF_LOCAL_KEY]

    add_entities([ToshibaClimateEntity(name, device_id, ip, localkey)], True)


ModeMap = {
    HVACMode.AUTO: ModeType.AutoMode,
    HVACMode.COOL: ModeType.CoolingMode,
    HVACMode.DRY: ModeType.DryingMode,
    HVACMode.HEAT: ModeType.HeatingMode,
    HVACMode.OFF: ModeType.PwrOffMode,
}

PresetMap = {
    PRESET_NONE: SpecialModeType.NoSpecialMode,
    PRESET_ECO: SpecialModeType.EcoSpecialMode,
    PRESET_BOOST: SpecialModeType.HiPowerSpecialMode,
}

FanMap = {
    FAN_AUTO: FanType.FanAuto,
    FAN_LOW: FanType.Fan1,
    FAN_MEDIUM: FanType.Fan3,
    FAN_HIGH: FanType.Fan5,
}


class ToshibaClimateEntity(ClimateEntity):
    """Toshiba Climate."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_mode = HVACMode.OFF
    _attr_target_temperature = 18
    _attr_max_temp = 26
    _attr_min_temp = 14
    _attr_target_temperature_step = 1
    _attr_fan_modes = [FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH]
    _attr_fan_mode = FAN_AUTO
    _attr_preset_modes = [PRESET_NONE, PRESET_ECO, PRESET_BOOST]
    _attr_preset_mode = PRESET_NONE
    status = {}

    def __init__(self, name, dev_id, ip, localkey) -> None:
        super().__init__()
        self._device_id = dev_id
        self._name = name
        self._device_ip = ip
        self._device_localkey = localkey
        self._attr_name = name
        self._attr_hvac_modes = [
            HVACMode.OFF,
            HVACMode.AUTO,
            HVACMode.HEAT,
            HVACMode.COOL,
            HVACMode.DRY,
        ]
        self._attr_should_poll = True
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.PRESET_MODE
        )

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self._device_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.unique_id)
            },
            name=self.name,
            manufacturer="emylo",
            model="Smart WiFi IR Remote",
            sw_version="0.0.1",
        )

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        self._attr_hvac_mode = hvac_mode
        await self.send_ir_command()

    async def async_set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        self._attr_preset_mode = preset_mode
        await self.send_ir_command()

    async def async_set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        self._attr_fan_mode = fan_mode
        await self.send_ir_command()

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        hvac_mode = kwargs[ATTR_HVAC_MODE]
        temp = kwargs[ATTR_TEMPERATURE]
        if temp is not None:
            self._attr_target_temperature = temp
        if hvac_mode is not None:
            self._attr_hvac_mode = hvac_mode
        await self.send_ir_command()

    @staticmethod
    def read_status(_device_id, _device_ip, _device_localkey) -> dict:
        """Read device status using Tuya endpoint."""
        try:
            _ir = Contrib.IRRemoteControlDevice(
                _device_id, _device_ip, _device_localkey
            )
            _ir.set_socketRetryLimit(1)
            _ir.set_socketRetryDelay(1)
            _ir.set_socketTimeout(5)
            status = _ir.status()
            return status["dps"]
        except RuntimeError:
            _LOGGER.error("Exception while read_status")
        return None

    @staticmethod
    def send_ir_key(_device_id, _device_ip, _device_localkey, data) -> None:
        """Read device status using Tuya endpoint."""
        try:
            _ir = Contrib.IRRemoteControlDevice(
                _device_id, _device_ip, _device_localkey
            )
            _ir.set_socketRetryLimit(1)
            _ir.set_socketRetryDelay(1)
            _ir.set_socketTimeout(5)
            head = "010ED80000000000030015004000AB"
            key = "01$$0048" + IRCodeGenerator.to_data_format(data) + "@$"
            _ir.send_key(head, key)
        except RuntimeError:
            _LOGGER.error("Exception while send_ir_key")

    async def send_ir_command(self) -> None:
        """Send IR command to Toshiba AC device"""
        mode = ModeMap.get(self._attr_hvac_mode)
        preset = PresetMap.get(self._attr_preset_mode)
        fan = FanMap.get(self._attr_fan_mode)
        temp = int(self._attr_target_temperature)
        data, _, _ = IRCodeGenerator.make_mode_fan_temp(
            UnitType.UnitA,
            mode,
            preset,
            fan,
            temp,
        )
        _LOGGER.info(
            "Mode %s , Preset %s, Fan %s, Temp %s",
            str(mode),
            str(preset),
            str(fan),
            str(temp),
        )
        await self.hass.async_add_executor_job(
            ft.partial(
                ToshibaClimateEntity.send_ir_key,
                self._device_id,
                self._device_ip,
                self._device_localkey,
                data,
            )
        )

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        status = await self.hass.async_add_executor_job(
            ft.partial(
                ToshibaClimateEntity.read_status,
                self._device_id,
                self._device_ip,
                self._device_localkey,
            )
        )
        if status is not None:
            self._attr_current_humidity = int(status["102"])
            self._attr_current_temperature = int(status["101"]) * 0.1
