import asyncio
import logging
import random

import requests
from requests import JSONDecodeError, RequestException

from app.api.config import configure_logging, settings

configure_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DummyPcsPerMinSender:

    def __init__(self, poller):
        self.poller = poller
        self.last_readings = {}

    async def send_readings(self):
        test_status = {
            'stop': [0 for _ in range(2 * 2)],
            'work': [random.randint(150, 200) for _ in range(2 * 2)],
            'offline': [None for _ in range(2 * 2)]
        }
        index = 0
        data = test_status[random.choice(list(test_status.keys()))]
        while True:
            for_sent = []
            if data[index] is not None:
                for_sent.append(
                    {
                        'sensor': 'test01',
                        'value': data[index],
                        # 'measured_at': current_reading.time.
                    }
                )
            logger.debug(f'{for_sent=}')
            index += 1
            if index == len(data):
                data = test_status[random.choice(list(test_status.keys()))]
                index = 0
            if for_sent:
                try:
                    logger.info('Отправка данных в PhyHub..')
                    response = requests.post(
                        url=settings.receiver_url,
                        headers={
                            'Authorization':
                                f'Token {settings.receiver_token}'},
                        json=for_sent
                    )
                    logger.info(response.json())
                except (RequestException, JSONDecodeError) as err:
                    logger.error(f'Ошибка отправки:\n{err}')
            await asyncio.sleep(30)
