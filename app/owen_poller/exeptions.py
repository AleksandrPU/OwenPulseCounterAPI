class DeviceNotFound(Exception):
    def __init__(self, device_name):
        super().__init__(f'Устройство "{device_name}" не найдено')
