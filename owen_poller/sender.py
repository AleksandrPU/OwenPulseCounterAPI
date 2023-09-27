import asyncio
import copy
from dataclasses import dataclass
from time import sleep
import requests

from owen_poller.owen_poller import SensorReading


class PcsPerMinSender:

    def __init__(self, poller):
        self.poller = poller
        self.last_readings = {}

    async def send_readings(self):
        while True:
            for_sent = []
            for sensor in self.poller.sensors.values():
                current_reading: SensorReading = sensor.reading
                if current_reading.value is None:
                    continue
                previous_reading: SensorReading = self.last_readings.get(
                    sensor.name)
                if previous_reading is None or previous_reading.value is None:
                    self.last_readings[sensor.name] = copy.copy(current_reading)
                    continue
                duration = current_reading.time - previous_reading.time
                if duration.total_seconds() <= 0:
                    continue
                speed = ((current_reading.value - previous_reading.value)
                         / duration.total_seconds()
                         * 60)
                for_sent.append(
                    {
                        'sensor': sensor.name,
                        'value': speed,
                        # 'measured_at': current_reading.time.
                    }
                )
                self.last_readings[sensor.name] = copy.copy(current_reading)
            response = requests.post(
                url='http://192.168.0.50/api/v1/create_readings/',
                headers={'Authorization': 'Token 395fb60d881adae2a1ec69f974da6958d44fb47b'},
                json=for_sent
            )
            await asyncio.sleep(30)
