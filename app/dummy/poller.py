import dataclasses
from dataclasses import dataclass
from datetime import datetime
from random import randint
from typing import Any

from serial import Serial

from app.api.common import SensorReading
from app.dummy.counter import DummyCounter


@dataclass
class DummySensor:
    name: str
    device: DummyCounter
    parameter_hash: bytes
    serial: Serial
    reading: SensorReading = dataclasses.field(default_factory=SensorReading)
    total_count: int = 0

    def update(self) -> None:
        self.total_count += randint(1, 3)
        self.reading.value = self.total_count
        self.reading.time = datetime.now()

    def get(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'reading': self.device.read_parameter(
                self.serial, self.parameter_hash),
            'reading_time': datetime.now(),
        }
