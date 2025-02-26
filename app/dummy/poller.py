import dataclasses
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from serial import Serial

from app.dummy.counter import DummyCounter
from app.owen_poller.owen_poller import SensorReading


@dataclass
class DummySensor:
    name: str
    device: DummyCounter
    parameter_hash: bytes
    serial: Serial
    reading: SensorReading = dataclasses.field(default_factory=SensorReading)

    def update(self) -> None:
        pass

    def get(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'reading': self.device.read_parameter(
                self.serial, self.parameter_hash),
            'reading_time': datetime.now(),
        }
