import random
from typing import Any

from serial import Serial

from app.owen_counter.exeptions import ImproperlyConfiguredError


class DummyCounter:
    TEST: bytes = b'\x00'

    PARAMS: dict[bytes, dict[str, Any]] = {
        TEST: {
            'response_len': 0,
            'converter': None
        },
    }

    __ADDR_ERR_MSG = (
        'Неверный адрес устройства: {actual}. '
        'Установите значение из диапазона: 0 - {max_addr}')
    __ADDR_LEN_ERR_MSG = (
        'Неверная длина адреса устройства: {actual}. '
        'Установите одно из значений: {expected}.')

    __current_status = None
    __values = None
    __index = 0

    def __init__(self, addr: int, addr_len: int = 8):
        """
        :param addr: адрес счетчика СИ8,
        :param addr_len: длина адреса.
        """
        # проверяем валидность addr_len
        if addr_len != 0:
            raise ImproperlyConfiguredError(
                self.__ADDR_LEN_ERR_MSG.format(
                    actual=addr_len,
                    expected=0
                )
            )
        self.addr_len = addr_len
        if addr != 0:
            raise ImproperlyConfiguredError(
                self.__ADDR_ERR_MSG.format(actual=addr, max_addr=0)
            )
        self.addr = addr

        work = [
            random.randint(150, 200) for _ in range(2 * random.randint(9, 10))]
        part_work = [
            random.randint(10, 100) for _ in range(2 * random.randint(5, 7))]
        pause = [random.randint(0, 9) for _ in range(2 * random.randint(2, 9))]
        stop = [
            random.randint(0, 9) for _ in range(2 * random.randint(11, 20))]
        offline = [None for _ in range(2 * random.randint(9, 12))]
        self.__values = (
            offline + stop + part_work + pause + stop + work + pause
            + part_work + work + stop + work + stop + offline)
        self.__index = 0

    def read_parameter(self, serial_if: Serial, parameter_hash: bytes):
        """
        Считывает параметр счетчика импульсов.
        :param serial_if: Порт.
        :param parameter_hash: Hash параметра счетчика.
        :return: Значение параметра.
        """

        value = self.__values[self.__index]
        self.__index += 1
        if self.__index >= len(self.__values):
            self.__index = 0
        return value
