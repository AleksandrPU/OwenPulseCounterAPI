import asyncio
from time import sleep

from serial import Serial

from . import settings
from owen_counter.owen_ci8 import OwenCI8


class CountersPoller:
    ERR_DEVICE_NOT_FOUND = 'Device "{name}" not found.'

    def __init__(self):
        self.serial_interface = Serial(**settings.serial_settings)
        self.devices = {}
        for device_name, device_settings in settings.devices.items():
            self.devices[device_name] = OwenCI8(**device_settings)

    async def poll(self):
        while True:
            for device in self.devices.values():
                try:
                    value = device.read_counter_parameter(
                        self.serial_interface, OwenCI8.DCNT)
                    print(value, device.bcd_to_int(value))
                    # await asyncio.sleep(0.79)
                    await asyncio.sleep(0.2)
                except Exception as err:
                    print(err)
                    # await asyncio.sleep(1)

    async def test_poll(self):
        i = 0
        while True:
            print(i)
            i += 1
            await asyncio.sleep(1)
