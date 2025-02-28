import asyncio
import copy
import dataclasses
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from serial import Serial

from app import settings
from app.api.common import SensorReading
from app.api.config import configure_logging
from app.dummy.counter import DummyCounter
from app.dummy.poller import DummySensor
from app.owen_counter.owen_ci8 import OwenCI8

from .exeptions import DeviceNotFound

configure_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
                type_sensor = DummySensor
                device = DummyCounter
            else:
                type_sensor = Sensor
                device = OwenCI8
            self.sensors[sensor_name] = type_sensor(
                name=sensor_name,
                device=device(addr=sensor_settings['addr'],
                              addr_len=sensor_settings['addr_len']),
                parameter_hash=sensor_settings['parameter'],
                serial=serial
            )
        self.last_readings = {}

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

    def get_list_readings(
            self, work_centers: list[str]
    ) -> list[dict[str, Any]]:
        for_sent = []
        for work_center in work_centers:
            response = {
                'sensor': work_center,
                'value': None,
                'measured_at': datetime.now(),
                'status': 'Not Found'
            }
            if not (sensor := self.sensors.get(work_center)):
                logger.error(f'Device {work_center} not found in settings.py')
                for_sent.append(response)
                continue
            current_reading: SensorReading = sensor.reading
            if current_reading.value is None:
                response['status'] = 'Offline'
                for_sent.append(response)
                continue
            previous_reading: SensorReading = self.last_readings.get(
                sensor.name)
            if previous_reading is None or previous_reading.value is None:
                self.last_readings[sensor.name] = copy.copy(
                    current_reading)
                response['status'] = 'OK'
                for_sent.append(response)
                continue
            duration = current_reading.time - previous_reading.time
            if duration.total_seconds() <= 0:
                continue
            speed = ((current_reading.value - previous_reading.value)
                     / duration.total_seconds()
                     * 60)
            response['value'] = speed
            response['status'] = 'OK'
            for_sent.append(response)
            self.last_readings[sensor.name] = copy.copy(current_reading)
        logger.debug(f'{for_sent=}')
        return for_sent
