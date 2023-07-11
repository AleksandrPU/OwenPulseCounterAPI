import asyncio

from serial import Serial

from owen_counter.owen_ci8 import OwenCI8
from . import settings


class CountersPoller:
    ERR_DEVICE_NOT_FOUND = 'Device "{name}" not found.'

    def __init__(self):
        self.serial_interface = Serial(**settings.serial_settings)
        self.serial_interface.close()
        self.serial_interface.open()
        self.devices = {}
        for device_name, device_settings in settings.devices.items():
            self.devices[device_name] = OwenCI8(**device_settings)

    async def poll(self):
        while True:
            for device in self.devices.values():
                try:
                    value = device.read_counter_parameter(
                        self.serial_interface, OwenCI8.DTMR)
                    print(value)
                    # await asyncio.sleep(0.79)
                    # await asyncio.sleep(0.1)
                except Exception as err:
                    print(err)
                    await asyncio.sleep(1)

    async def test_poll(self):
        i = 0
        while True:
            print(i)
            i += 1
            await asyncio.sleep(1)
