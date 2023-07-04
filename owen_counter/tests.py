from collections import namedtuple
import unittest

from owen_ci8 import OwenCI8
from exeptions import ImproperlyConfiguredError


class TestOwenCounter(unittest.TestCase):
    """
    Тест класса OwenCI8.
    """

    def test_init_with_invalid_addr_len(self):
        """Тестируем конструктор с невалидными значениями addr_len."""
        valid_values = (8, 11)
        for no_valid_value in range(-1, 33):
            if no_valid_value in valid_values:
                continue
            with self.subTest(addr_len=no_valid_value):
                with self.assertRaises(
                        ImproperlyConfiguredError,
                        msg='Конструктор не поднимает исключение!'):
                    OwenCI8(addr=0, addr_len=no_valid_value)

    def test_init_with_invalid_addr(self):
        """Тестируем конструктор с невалидными значениями addr."""
        Fixture = namedtuple('Fixture', ['addr', 'addr_len'])
        fixtures = [
            Fixture(addr=-1, addr_len=8),
            Fixture(addr=256, addr_len=8),
            Fixture(addr=-1, addr_len=11),
            Fixture(addr=2048, addr_len=11)
        ]
        for fixture in fixtures:
            with self.subTest(addr=fixture.addr, addr_len=fixture.addr_len):
                with self.assertRaises(
                        ImproperlyConfiguredError,
                        msg='Конструктор не поднимает исключение!'):
                    OwenCI8(addr=fixture.addr, addr_len=fixture.addr_len)

    def test_init_addr_translation(self):
        """Тестируем трансляцию addr конструктором."""
        Fixture = namedtuple('Fixture',
                             ['addr', 'addr_len', 'addr_translated'])
        fixtures = [
            Fixture(addr=0x00, addr_len=8, addr_translated=b'\x00\x00'),
            Fixture(addr=0xFF, addr_len=8, addr_translated=b'\xFF\x00'),
            Fixture(addr=0xA3, addr_len=8, addr_translated=b'\xA3\x00'),
            Fixture(addr=0x00, addr_len=11, addr_translated=b'\x00\x00'),
            Fixture(addr=0x7FF, addr_len=11, addr_translated=b'\xFF\xE0'),
            Fixture(addr=0x555, addr_len=11, addr_translated=b'\xAA\xA0'),
        ]
        for fixture in fixtures:
            instance = OwenCI8(addr=fixture.addr,
                               addr_len=fixture.addr_len)
            with self.subTest(addr=fixture.addr,
                              addr_len=fixture.addr_len,
                              addr_translated=fixture.addr_translated):
                self.assertEqual(fixture.addr_translated,
                                 instance.addr,
                                 'Неверное значение self.addr.')

    def test_calc_owen_crc(self):
        """Тестируем правильность расчета CRC."""
        Fixture = namedtuple('Fixture', ['data', 'crc'])
        fixtures = [
            Fixture(data=b'', crc=b'\x00\x00'),
            Fixture(data=b'\00', crc=b'\x00\x00'),
            Fixture(data=b'\01', crc=b'\x8F\x57'),
            Fixture(data=b'\xFF', crc=b'\x18\x2A'),
            Fixture(data=b'\x01\xFF', crc=b'\xBF\x03'),
            Fixture(data=b'\x01\xFF\xA0', crc=b'\x44\x7B'),
            Fixture(data=b'DFJJKNKLF1&WLKEFFNEKRJFNKEJRN', crc=b'\x71\xBE'),
        ]
        for fixture in fixtures:
            with self.subTest(data=fixture.data):
                call = (OwenCI8(addr=0, addr_len=8)
                        .calc_owen_crc(fixture.data))
                self.assertEqual(fixture.crc, call, msg='Неверный CRC!')

    def test_get_command_packet(self):
        """Тестируем правильность формирования пакета команды."""
        Fixture = namedtuple('Fixture',
                             ['addr', 'addr_len', 'data', 'expected_packet'])
        fixtures = [
            # запрос DCNT
            Fixture(addr=0x02,
                    addr_len=8,
                    data=b'\xC1\x73',
                    expected_packet=b'\x02\x10\xC1\x73\xE7\x1A'),
            # запрос DSPD
            Fixture(addr=0x0F,
                    addr_len=8,
                    data=b'\x8F\xC2',
                    expected_packet=b'\x0F\x10\x8F\xC2\x13\x56'),
            # запрос DTMR
            Fixture(addr=0x0A,
                    addr_len=8,
                    data=b'\xE6\x9C',
                    expected_packet=b'\x0A\x10\xE6\x9C\x85\x63'),
            # запрос DCNT
            Fixture(addr=0x00,
                    addr_len=11,
                    data=b'\xC1\x73',
                    expected_packet=b'\x00\x10\xC1\x73\x92\xE6'),

            # запрос DSPD
            Fixture(addr=0x7FF,
                    addr_len=11,
                    data=b'\x8F\xC2',
                    expected_packet=b'\xFF\xF0\x8F\xC2\x02\x71'),
            # запрос DTMR
            Fixture(addr=0x222,
                    addr_len=11,
                    data=b'\xE6\x9C',
                    expected_packet=b'\x44\x50\xE6\x9C\xDE\x15'),
        ]
        for fixture in fixtures:
            with self.subTest(addr=fixture.addr,
                              addr_len=fixture.addr_len,
                              data=fixture.data):
                call = (OwenCI8(addr=fixture.addr,
                                addr_len=fixture.addr_len)
                        .get_command_packet(parameter=fixture.data))
                self.assertEqual(fixture.expected_packet,
                                 call,
                                 'Сформирован неверный пакет!')

    def test_get_command_packet_with_invalid_parameter_len(self):
        """Тестируем поднятие ValueError, когда len(parameter) != 2."""
        invalid_parameters = [b'', b'\x00', b'abc', b'aaaaaaaa']
        for invalid_parameter in invalid_parameters:
            with self.subTest(parameter=invalid_parameter):
                with self.assertRaises(
                        ValueError,
                        msg='Исключение ValueError не поднято:'):
                    (OwenCI8(addr=1, addr_len=8)
                     .get_command_packet(parameter=invalid_parameter))

    def test_packet_to_ascii(self):
        """Тестируем преобразование двоичного пакета в ASCII пакет."""
        Fixture = namedtuple('Fixture', ['data', 'ascii'])
        fixtures = [
            Fixture(data=b'', ascii=b'\x23\x0d'),
            Fixture(data=b'\x0E', ascii=b'\x23\x47\x55\x0d'),
            # запрос DCNT
            Fixture(data=b'\x05\x10\xC1\x73\x43\xE0',
                    ascii=b'#GLHGSHNJKJUG\r'),
        ]
        for fixture in fixtures:
            with self.subTest(data=fixture.data):
                call = (OwenCI8(addr=1, addr_len=8)
                        .packet_to_ascii(bytearray(fixture.data)))
                self.assertEqual(fixture.ascii, call,
                                 'Сформирован неверный пакет!')


if __name__ == '__main__':
    unittest.main()
