import asyncio
import dataclasses
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from serial import Serial

from app.owen_counter.owen_ci8 import OwenCI8

from app import settings
from .exeptions import DeviceNotFound
from ..api.config import configure_logging
from ..owen_counter.test_counter import TestCounter

configure_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class SensorReading:
    value: Any = None
    time: datetime = datetime.now()


@dataclass
class Sensor:
    name: str
    device: OwenCI8
    parameter_hash: bytes
    serial: Serial
    reading: SensorReading = dataclasses.field(default_factory=SensorReading)
    # reading_time: datetime = datetime.now()

    def update(self) -> None:
        try:
            self.reading.value = self.device.read_parameter(
                self.serial, self.parameter_hash)
            self.reading.time = datetime.now()
        except Exception as err:
            logger.error(f'Сенсор {self.name} {err}')

    def get(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'reading': self.reading.value,
            'reading_time': self.reading.time
        }


class SensorsPoller:

    def __init__(self):
        if settings.serial_settings:
            serial = Serial(**settings.serial_settings)
            serial.close()
            serial.open()
        else:
            serial = None
        self.sensors: dict[str, Sensor] = {}
        for sensor_settings in settings.sensors_settings:
            sensor_name = sensor_settings['name']
            if sensor_settings['addr'] == 0:
                device = TestCounter
            else:
                device = OwenCI8
            self.sensors[sensor_name] = Sensor(
                name=sensor_name,
                # device=OwenCI8(addr=sensor_settings['addr'],
                #                addr_len=sensor_settings['addr_len']),
                device=device(addr=sensor_settings['addr'],
                              addr_len=sensor_settings['addr_len']),
                parameter_hash=sensor_settings['parameter'],
                serial=serial
            )

    async def poll(self):
        """
        Цикл опроса устройств.
        """
        while True:
            for sensor in self.sensors.values():
                await asyncio.sleep(0)
                sensor.update()
            await asyncio.sleep(settings.POLL_DELAY)

    def get_sensor_readings(self, sensor_name: str) -> dict[str, Any]:
        try:
            return self.sensors[sensor_name].get()
        except KeyError:
            raise DeviceNotFound(sensor_name)
