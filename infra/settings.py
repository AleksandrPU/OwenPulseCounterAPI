from typing import Any

from app.dummy.counter import DummyCounter

serial_settings: dict[str, Any] = {
    # 'port': '/dev/ttyUSB0',
    # 'baudrate': 9600,
    # 'bytesize': 8,
    # 'parity': 'N',
    # 'stopbits': 1,
    # 'timeout': 0.2
}

sensors_settings: list[dict[str, Any]] = [
    # {
    #     'name': 's10',
    #     'addr': 1,
    #     'addr_len': 8,
    #     'parameter': OwenCI8.DCNT
    # },
    # {
    #     'name': 's11',
    #     'addr': 2,
    #     'addr_len': 8,
    #     'parameter': OwenCI8.DCNT
    # },
    # {
    #     'name': 's20',
    #     'addr': 3,
    #     'addr_len': 8,
    #     'parameter': OwenCI8.DCNT
    # },
    # {
    #     'name': 's21',
    #     'addr': 4,
    #     'addr_len': 8,
    #     'parameter': OwenCI8.DCNT
    # },
    {
        'name': 'test1',
        'addr': 0,
        'addr_len': 0,
        'parameter': DummyCounter.TEST
    },
]

POLL_DELAY = 0.5
