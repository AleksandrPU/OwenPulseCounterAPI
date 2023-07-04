from serial import Serial

from owen_counter.exeptions import ImproperlyConfiguredError


class OwenCI8:

    PARAM_DCNT = b'\xC1\x73'
    PARAM_DSPD = b'\x8F\xC2'
    PARAM_DTMR = b'\xE6\x9C'

    ADDR_LENS = (8, 11)

    ADDR_LEN_ERR_MSG = (f'Неверное значение addr={{addr_len}}. '
                        f'Установите одно из значений - {ADDR_LENS}')
    ADDR_ERR_MSG = ('Неверный адрес устройства. '
                    'Установите значение из диапазона 0 - {max_addr}')
    PARAM_LEN_ERR_MSG = ('Неверная длина значения parameter '
                         '(len(parameter) != 2).')

    def __init__(self, addr: int, addr_len: int = 8):
        """
        :param addr: адрес счетчика,
        :param addr_len:
        """
        # проверяем валидность addr_len
        if addr_len not in self.ADDR_LENS:
            raise ImproperlyConfiguredError(
                self.ADDR_LEN_ERR_MSG.format(addr_len=addr_len))
        self.addr_len = addr_len
        # проверяем валидность адреса, разделяем на байты
        max_addr = 2 ** addr_len - 1
        if not isinstance(addr, int) or not 0 <= addr <= max_addr:
            raise ImproperlyConfiguredError(
                self.ADDR_ERR_MSG.format(max_addr=max_addr))
        addr <<= (8 - addr_len + 8)
        self.addr = addr.to_bytes(2, 'big')
        pass

    @staticmethod
    def calc_owen_crc(data: bytes) -> bytes:
        """
        Возвращает ОВЕН CRC16. Полином 0x8F57.
        :param data:
        :return:
        """
        crc = 0
        for byte in data:
            for j in range(8):
                if (byte ^ (crc >> 8)) & 0x80:
                    crc <<= 1
                    crc ^= 0x8F57
                else:
                    crc <<= 1
                byte <<= 1
                byte &= 0xff
                crc &= 0xffff
        return crc.to_bytes(2, 'big')

    def get_command_packet(self, parameter: bytes) -> bytearray:
        """
        Подготавливает двоичный пакет запроса парамера.
        Пакет содержит поля адреса, признака запроса и CRC.
        :param parameter: Hash запрашиваемого параметра.
        :return: Двоичный пакет.
        """
        if len(parameter) != 2:
            raise ValueError(self.PARAM_LEN_ERR_MSG)
        # адрес + hash параметра счетчика
        data: bytearray = bytearray(self.addr) + parameter
        # устанавливаем бит запроса, размер блока данных = 0
        data[1] |= 0x10
        # добавляем CRC
        data += self.calc_owen_crc(data)
        return data

    @staticmethod
    def packet_to_ascii(data: bytearray) -> bytearray:
        """
        Преобразует двоичный пакет в ASCII.
        Каждая тетрада пакета заменяется на ASCII символ с кодом 0x47 - 0x56.
        Добавляет символы начала (#) и окончания (CR) пакета.
        """
        ascii_packet = bytearray(b'#')
        for char in data:
            char = int(char)
            l_n = (char & 0x0F) + 0x47
            h_n = ((char & 0xF0) >> 4) + 0x47
            ascii_packet.append(h_n)
            ascii_packet.append(l_n)
        ascii_packet.append(0x0D)
        return ascii_packet

    def read_counter_parameter(self, ser: Serial, parameter: bytes):
        """
        Считывает параметр счетчика импульсов.
        :param ser: Порт.
        :param parameter: Hash параметра счетчика.
        :return: Значение параметра.
        """
        bin_packet = self.get_command_packet(parameter)
        ascii_packet = self.packet_to_ascii(bin_packet)
        ser.write(ascii_packet)
        received_data = ser.read(22)
        return received_data
