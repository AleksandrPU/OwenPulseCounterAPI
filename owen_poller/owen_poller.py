import asyncio
from typing import Any

from serial import Serial

from owen_counter.owen_ci8 import OwenCI8
from . import settings
from .exeptions import DeviceNotFound


class CountersPoller:
    ERR_DEVICE_NOT_FOUND = 'Device "{name}" not found.'

    def __init__(self):
        self.serial_interface = Serial(**settings.serial_settings)
        self.serial_interface.close()
        self.serial_interface.open()
        self.devices: dict[str, OwenCI8] = {}
        self.devices_params: dict[str, dict[bytes, Any]] = {}
        for device_settings in settings.device_settings:
            device_name = device_settings['name']
            self.devices[device_name] = OwenCI8(
                addr=device_settings['addr'],
                addr_len=device_settings['addr_len']
            )
            self.devices_params[device_name] = dict.fromkeys(
                device_settings['params'])

    async def poll(self):
        """
        Цикл опроса устройств.
        """
        while True:
            for device_name, device in self.devices.items():
                params = self.devices_params[device_name]
                for param in params:
                    try:
                        params[param] = device.read_parameter(
                            self.serial_interface, param)
                    except Exception as err:
                        print(err)
                        await asyncio.sleep(0.5)
                await asyncio.sleep(1)

    def get_params(self, device_name: str) -> dict:
        try:
            return self.devices_params[device_name]
        except KeyError:
            raise DeviceNotFound(device_name)
