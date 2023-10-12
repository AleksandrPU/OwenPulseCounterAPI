import asyncio
import copy
import requests
from requests import JSONDecodeError, RequestException

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
            try:
                print('Отправка данных в PhyHub..')
                print(for_sent)
                response = requests.post(
                    url='http://phyhub.polipak.local/api/v1/create_readings/',
                    # url='http://127.0.0.1:8000/api/v1/create_readings/',
                    headers={'Authorization': 'Token e441b27fb5a4a83e80e29d958fdf08f9b919448d'},
                    # headers={'Authorization': 'Token 90386e054c5c229d4cbcfde73cfc81e6304f4e51'},
                    json=for_sent
                )
                print(response.json())
            except (RequestException, JSONDecodeError) as err:
                print('Ошибка отправки')
                print(err)
            await asyncio.sleep(30)
