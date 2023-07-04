from typing import Optional

from serial import Serial

import settings
from owen_counter.owen_ci8 import OwenCI8


class SerialInterface(Serial):

    def read_data(self) -> Optional[bytes]:
        return self.read()


class CountersPoller:
    ERR_DEVICE_NOT_FOUND = 'Device "{name}" not found.'

    def __init__(self):
        self.serial_interface = SerialInterface(**settings.serial_settings)
        self.devices = {}
        for device_name, device_settings in settings.devices.items():
            self.devices[device_name] = OwenCI8(**device_settings)
