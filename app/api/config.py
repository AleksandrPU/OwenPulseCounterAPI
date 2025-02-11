import logging
import os

from pydantic import BaseSettings, HttpUrl


class Settings(BaseSettings):
    receiver_url: HttpUrl
    receiver_token: str
    poller_active: bool = False
    test_poller: bool = False

    class Config:
        # env_file = '.env'
        env_file = f'{os.path.dirname(os.path.abspath(__file__))}/.env'
        env_file_encoding = 'utf-8'


def configure_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d '
               '%(levelname)-7s - %(message)s',
    )


settings = Settings()
