import json
from dataclasses import dataclass, asdict, field
from typing import Any


@dataclass
class ServoPinConfig:
    role: str = "Link"
    pin: int = 0
    angle_offset: float = 0.0
    min_angle: float = 0.0
    max_angle: float = 360.0
    deadband_degrees: float = 1.5
    command_interval_seconds: float = 0.08


@dataclass
class ServoPinsConfig:
    linkage_hold_time: float = 1.0
    defaults: ServoPinConfig = field(
        default_factory=lambda: ServoPinConfig(role="Default", pin=0)
    )
    servos: list[ServoPinConfig] = field(
        default_factory=lambda: [
            ServoPinConfig(role="Link", pin=15),
            ServoPinConfig(role="Arm", pin=14),
            ServoPinConfig(role="Pump", pin=4),
        ]
    )


@dataclass
class YoloConfig:
    enabled: bool = True
    path: str = "assets/main.pt"
    min_confidence: float = 0.4


@dataclass
class CaptureConfig:
    resolution: dict[str, int] = field(
        default_factory=lambda: {
            "x": 800,
            "y": 600,
        }
    )
    enabled: bool = True
    capture_fps: int = 10
    use_webcam: bool = True
    ip_address: str = "http://192.168.100.109:8080/video"


@dataclass
class Config:
    servo_pins: ServoPinsConfig = field(default_factory=ServoPinsConfig)
    yolo: YoloConfig = field(default_factory=YoloConfig)
    capture: CaptureConfig = field(default_factory=CaptureConfig)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=4)

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        servo_data = data.get("servo_pins", {})
        defaults = ServoPinConfig(**servo_data.get("defaults", {}))
        servos = [ServoPinConfig(**item) for item in servo_data.get("servos", [])]

        return cls(
            servo_pins=ServoPinsConfig(
                linkage_hold_time=float(servo_data.get("linkage_hold_time", 1.0)),
                defaults=defaults,
                servos=servos
                if servos
                else [
                    ServoPinConfig(role="Link", pin=15),
                    ServoPinConfig(role="Arm", pin=14),
                    ServoPinConfig(role="Pump", pin=4),
                ],
            ),
            yolo=YoloConfig(**data.get("yolo", {})),
            capture=CaptureConfig(**data.get("capture", {})),
        )

    @classmethod
    def load_from_file(cls, path: str):
        try:
            with open(path, "r") as file:
                data = json.load(file)
                return cls.from_dict(data)
        except Exception:
            config = cls()
            config.save_to_file(path)
            return config

    def save_to_file(self, path: str):
        with open(path, "w") as file:
            file.write(self.to_json())
