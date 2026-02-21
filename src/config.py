import json
from dataclasses import dataclass, asdict, field
from typing import Any


@dataclass
class ServoPinsConfig:
    linkages: list[int] = field(default_factory=lambda: [15])
    linkage_hold_time: int = 1
    arms: list[int] = field(default_factory=lambda: [14])
    pumps: list[int] = field(default_factory=lambda: [4])


@dataclass
class YoloConfig:
    enabled: bool = True
    path: str = ""
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
        return cls(
            servo_pins=ServoPinsConfig(**data.get("servo_pins", {})),
            yolo=YoloConfig(**data.get("yolo", {})),
            capture=CaptureConfig(**data.get("capture", {})),
        )

    @classmethod
    def load_from_file(cls, path: str):
        try:
            with open(path, "r") as file:
                data = json.load(file)
                return cls.from_dict(data)
        except:
            config = cls()
            config.save_to_file(path)
            return config

    def save_to_file(self, path: str):
        with open(path, "w") as file:
            file.write(self.to_json())
