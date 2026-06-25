import json
from dataclasses import dataclass, asdict, field
from typing import Any
from enum import IntEnum


class ServoType(IntEnum):
    BASE_ARM = 0
    MID_ARM = 1
    TOP_ARM = 2


@dataclass
class MotorConfig:
    enabled: bool = True
    pin: int = 0
    min_speed: float = 0
    max_speed: float = 1.0
    left: bool = True
    reversed: bool = False


@dataclass
class ServoConfig:
    enabled: bool = True
    pin: int = 0
    type: int = ServoType.BASE_ARM.value
    min_angle: float = 0.0
    max_angle: float = 360.0
    offset: float = 0.0
    deadband: float = 1.5
    interval: float = 0.08


@dataclass
class PumpConfig:
    enabled: bool = True
    forward_pin: int = 0
    backward_pin: int = 0
    enable_pin: int = 0


@dataclass
class CaptureConfig:
    enabled: bool = True
    fps: int = 30
    forward_source: int | str = 0
    backward_source: int | str = 0
    arm_source: int | str = 0


@dataclass
class YoloConfig:
    enabled: bool = True
    model_path: str = "assets/main.pt"
    min_confidence: float = 0.4


@dataclass
class Config:
    capture: CaptureConfig = field(default_factory=CaptureConfig)
    yolo: YoloConfig = field(default_factory=YoloConfig)
    motors_enabled: bool = True
    motors: list[MotorConfig] = field(
        default_factory=lambda: [
            MotorConfig(
                enabled=True,
                pin=12,
                min_speed=0,
                max_speed=1.0,
                left=True,
                reversed=False,
            ),
            MotorConfig(
                enabled=True,
                pin=13,
                min_speed=0,
                max_speed=1.0,
                left=False,
                reversed=True,
            ),
        ]
    )
    pumps_enabled: bool = True
    pumps: list[PumpConfig] = field(
        default_factory=lambda: [
            PumpConfig(enabled=True, forward_pin=25, backward_pin=24, enable_pin=9),
        ]
    )
    servos_enabled: bool = True
    servos: list[ServoConfig] = field(
        default_factory=lambda: [
            ServoConfig(
                enabled=True,
                pin=6,
                type=ServoType.BASE_ARM.value,
                min_angle=0,
                max_angle=360,
                offset=0,
                deadband=1.5,
                interval=0.08,
            ),
            ServoConfig(
                enabled=True,
                pin=5,
                type=ServoType.MID_ARM.value,
                min_angle=0,
                max_angle=270,
                offset=0,
                deadband=1.5,
                interval=0.08,
            ),
            ServoConfig(
                enabled=True,
                pin=26,
                type=ServoType.TOP_ARM.value,
                min_angle=0,
                max_angle=270,
                offset=0,
                deadband=1.5,
                interval=0.08,
            ),
        ]
    )

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=4)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        capture_data = data.get("capture", {})
        yolo_data = data.get("yolo", {})
        motors_data = data.get("motors", [])
        servos_data = data.get("servos", [])
        pumps_data = data.get("pumps", [])

        return cls(
            capture=CaptureConfig(
                enabled=capture_data.get("enabled", True),
                fps=capture_data.get("fps", 30),
                forward_source=capture_data.get("forward_source", 0),
                backward_source=capture_data.get("backward_source", 0),
                arm_source=capture_data.get("arm_source", 0),
            ),
            yolo=YoloConfig(
                enabled=yolo_data.get("enabled", True),
                model_path=yolo_data.get("model_path", "assets/main.pt"),
                min_confidence=yolo_data.get("min_confidence", 0.4),
            ),
            motors_enabled=data.get("motors_enabled", True),
            motors=[MotorConfig(**motor) for motor in motors_data]
            if motors_data
            else cls().motors,
            servos_enabled=data.get("servos_enabled", True),
            servos=[ServoConfig(**servo) for servo in servos_data]
            if servos_data
            else cls().servos,
            pumps_enabled=data.get("pumps_enabled", True),
            pumps=[PumpConfig(**pump) for pump in pumps_data]
            if pumps_data
            else cls().pumps,
        )

    @classmethod
    def load_from_file(cls, path: str = "config.json") -> "Config":
        try:
            with open(path, "r") as file:
                data = json.load(file)
                return cls.from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError, Exception):
            config = cls()
            config.save_to_file(path)
            return config

    def save_to_file(self, path: str = "config.json"):
        with open(path, "w") as file:
            file.write(self.to_json())
