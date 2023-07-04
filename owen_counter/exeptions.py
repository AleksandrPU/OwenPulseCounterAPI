class ImproperlyConfiguredError(Exception):

    def __init__(self, message):
        super().__init__(self, f'Ошибка конфигурации устройства. {message}')
