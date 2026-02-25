import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
import cv2
import numpy as np
from config import CaptureConfig, ServoPinConfig, ServoPinsConfig, YoloConfig

MAX_SPRAY_TIME = 5.0
ARM_HEIGHT_INTERVALS = 3
DEFAULT_YOLO_MODEL_PATH = "assets/main.pt"


@dataclass
class DetectionBox:
    x1: int
    y1: int
    x2: int
    y2: int
    confidence: float
    label: str


@dataclass
class DetectionResult:
    severity: float
    boxes: list[DetectionBox]
    active: bool
    reason: str = ""


class ServoChannel:
    def __init__(
        self,
        pin: int,
        *,
        min_angle: float = 0,
        max_angle: float = 360,
        angle_offset: float = 0.0,
        deadband_degrees: float = 1.5,
        min_command_interval: float = 0.08,
    ):
        self.pin = pin
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.angle_offset = angle_offset
        self.deadband_degrees = deadband_degrees
        self.min_command_interval = min_command_interval
        self.last_commanded_angle: float | None = None
        self.last_command_time = 0.0

        self.servo = None
        self.is_available = False
        self.init_error: str | None = None

        try:
            from gpiozero import AngularServo
            from gpiozero.pins.pigpio import PiGPIOFactory

            self.servo = AngularServo(
                pin,
                min_angle=min_angle,
                max_angle=max_angle,
                min_pulse_width=0.5 / 1000,
                max_pulse_width=2.5 / 1000,
                pin_factory=PiGPIOFactory(),
            )
            self.is_available = True
        except Exception as exc:
            try:
                from gpiozero import AngularServo

                self.servo = AngularServo(
                    pin,
                    min_angle=min_angle,
                    max_angle=max_angle,
                    min_pulse_width=0.5 / 1000,
                    max_pulse_width=2.5 / 1000,
                )
                self.is_available = True
            except Exception as fallback_exc:
                self.is_available = False
                self.init_error = f"pigpio={exc}; fallback={fallback_exc}"

    @property
    def available(self) -> bool:
        return self.is_available

    def set_angle(self, angle: float, force: bool = False):
        if not self.is_available:
            return

        now = time.monotonic()
        calibrated_angle = angle + self.angle_offset
        bounded_angle = max(self.min_angle, min(calibrated_angle, self.max_angle))

        if not force and self.last_commanded_angle is not None:
            if abs(bounded_angle - self.last_commanded_angle) < self.deadband_degrees:
                return
            if now - self.last_command_time < self.min_command_interval:
                return

        self.servo.angle = bounded_angle
        self.last_commanded_angle = bounded_angle
        self.last_command_time = now

    def close(self):
        if not self.is_available:
            return
        try:
            self.servo.detach()
        except Exception:
            pass


class ServoRig:
    def __init__(self, config: ServoPinsConfig):
        self._lock = threading.RLock()
        self.linkages: list[ServoChannel] = []
        self.arms: list[ServoChannel] = []
        self.pumps: list[ServoChannel] = []

        self.linkage_hold_time = float(config.linkage_hold_time)
        self.linkages_active = False
        self.pumps_active = False
        self._setup(config)

    def _setup(self, config: ServoPinsConfig):
        self.shutdown()
        self.linkage_hold_time = float(config.linkage_hold_time)
        self.linkages = [
            self.build_channel(servo_cfg, config.defaults)
            for servo_cfg in config.servos
            if servo_cfg.role == "Link"
        ]
        self.arms = [
            self.build_channel(servo_cfg, config.defaults)
            for servo_cfg in config.servos
            if servo_cfg.role == "Arm"
        ]
        self.pumps = [
            self.build_channel(servo_cfg, config.defaults)
            for servo_cfg in config.servos
            if servo_cfg.role == "Pump"
        ]

    def build_channel(
        self, servo_cfg: ServoPinConfig, default_cfg: ServoPinConfig
    ) -> ServoChannel:
        min_angle = float(
            servo_cfg.min_angle
            if servo_cfg.min_angle is not None
            else default_cfg.min_angle
        )
        max_angle = float(
            servo_cfg.max_angle
            if servo_cfg.max_angle is not None
            else default_cfg.max_angle
        )
        if max_angle < min_angle:
            min_angle, max_angle = max_angle, min_angle

        return ServoChannel(
            servo_cfg.pin,
            min_angle=min_angle,
            max_angle=max_angle,
            angle_offset=float(
                servo_cfg.angle_offset
                if servo_cfg.angle_offset is not None
                else default_cfg.angle_offset
            ),
            deadband_degrees=max(
                0.0,
                float(
                    servo_cfg.deadband_degrees
                    if servo_cfg.deadband_degrees is not None
                    else default_cfg.deadband_degrees
                ),
            ),
            min_command_interval=max(
                0.0,
                float(
                    servo_cfg.command_interval_seconds
                    if servo_cfg.command_interval_seconds is not None
                    else default_cfg.command_interval_seconds
                ),
            ),
        )

    def apply_config(self, config: ServoPinsConfig):
        with self._lock:
            self._setup(config)
            self.set_linkages(False, force=True)
            self.set_pumps(False, force=True)
            self.set_arm_height(0.0, force=True)

    def set_linkages(self, active: bool, force: bool = False):
        with self._lock:
            self.linkages_active = active
            target = 30 if active else 0
            for servo in self.linkages:
                servo.set_angle(target, force=force)

    def set_arm_height(self, percent: float, force: bool = False):
        with self._lock:
            normalized = max(0.0, min(percent, 1.0))
            target = normalized * 70
            for servo in self.arms:
                servo.set_angle(target, force=force)

    def set_pumps(self, active: bool, force: bool = False):
        with self._lock:
            self.pumps_active = active
            target = 50 if active else 0
            for servo in self.pumps:
                servo.set_angle(target, force=force)

    def shutdown(self):
        for channel in [*self.linkages, *self.arms, *self.pumps]:
            channel.close()
        self.linkages = []
        self.arms = []
        self.pumps = []

    def manual_targets(self) -> list[str]:
        targets: list[str] = []
        for role, channels in (
            ("Link", self.linkages),
            ("Arm", self.arms),
            ("Pump", self.pumps),
        ):
            for channel in channels:
                targets.append(f"{role}:{channel.pin}")
        return targets

    def set_manual_angle(self, target: str, angle: float, force: bool = True) -> bool:
        try:
            role, pin_text = target.split(":", 1)
            pin = int(pin_text)
        except Exception:
            return False

        channels: list[ServoChannel]
        if role == "Link":
            channels = self.linkages
        elif role == "Arm":
            channels = self.arms
        elif role == "Pump":
            channels = self.pumps
        else:
            return False

        for channel in channels:
            if channel.pin == pin:
                channel.set_angle(angle, force=force)
                return True
        return False

    @property
    def total_channels(self) -> int:
        return len(self.linkages) + len(self.arms) + len(self.pumps)

    @property
    def available_channels(self) -> int:
        channels = [*self.linkages, *self.arms, *self.pumps]
        return sum(1 for channel in channels if channel.available)


class CaptureManager:
    def __init__(self, config: CaptureConfig):
        self._lock = threading.Lock()
        self.capture: cv2.VideoCapture | None = None
        self.config = config
        self.apply(config)

    def source(self, config: CaptureConfig):
        if config.use_webcam:
            return 0
        return config.ip_address

    def apply(self, config: CaptureConfig):
        self.config = config
        if self.capture:
            self.capture.release()
            self.capture = None

        if not config.enabled:
            return

        self.capture = cv2.VideoCapture(self.source(config))

    def apply_config(self, config: CaptureConfig):
        with self._lock:
            must_reopen = (
                self.capture is None
                or config.enabled != self.config.enabled
                or config.use_webcam != self.config.use_webcam
                or config.ip_address != self.config.ip_address
            )
            if must_reopen:
                self.apply(config)
            else:
                self.config = config

    def read(self) -> np.ndarray | None:
        with self._lock:
            if not self.config.enabled or self.capture is None:
                return None
            ok, frame = self.capture.read()
            if not ok:
                return None
            width = self.config.resolution["x"]
            height = self.config.resolution["y"]
            return cv2.resize(frame, (width, height))

    def close(self):
        with self._lock:
            if self.capture:
                self.capture.release()
                self.capture = None


class YoloDetector:
    def __init__(self, config: YoloConfig):
        self.model = None
        self.config = config
        self.status_reason = ""
        self.load(config)

    def load(self, config: YoloConfig):
        self.config = config
        self.model = None
        self.status_reason = ""

        if not config.enabled:
            self.status_reason = "YOLO disabled"
            return
        model_path = self.resolve_model_path(
            config.path.strip() or DEFAULT_YOLO_MODEL_PATH
        )

        try:
            from ultralytics import YOLO

            self.model = YOLO(model_path)
        except Exception as exc:
            self.model = None
            self.status_reason = f"YOLO unavailable: {exc}"

    @staticmethod
    def resolve_model_path(path_value: str) -> str:
        path = Path(path_value)
        if path.is_absolute():
            return str(path)

        candidates: list[Path] = []
        if path_value.startswith("assets/") or path_value.startswith("assets\\"):
            candidates.append(Path(__file__).resolve().parent.parent / path)
        candidates.append(Path.cwd() / path)
        candidates.append(Path(__file__).resolve().parent / path)

        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        return str(candidates[0])

    def apply_config(self, config: YoloConfig):
        reload_required = (
            config.enabled != self.config.enabled
            or config.path != self.config.path
            or config.min_confidence != self.config.min_confidence
        )
        if reload_required:
            self.load(config)
        else:
            self.config = config

    def detect(self, frame: np.ndarray | None) -> DetectionResult:
        if frame is None:
            return DetectionResult(0.0, [], False, "Capture disabled")
        if not self.config.enabled:
            return DetectionResult(0.0, [], False, "YOLO disabled")
        if self.model is None:
            return DetectionResult(0.0, [], False, self.status_reason)

        try:
            infer = self.model(frame, verbose=False)
            result = infer[0]
            boxes = []

            confidences: list[float] = []
            names = getattr(result, "names", {})
            for detection in result.boxes:
                confidence = float(detection.conf.item())
                if confidence < self.config.min_confidence:
                    continue

                xyxy = detection.xyxy[0].tolist()
                class_id = (
                    int(detection.cls.item()) if detection.cls is not None else -1
                )
                _label: str = (
                    names.get(class_id, str(class_id))
                    if isinstance(names, dict)
                    else str(class_id)
                )
                boxes.append(
                    DetectionBox(
                        x1=int(xyxy[0]),
                        y1=int(xyxy[1]),
                        x2=int(xyxy[2]),
                        y2=int(xyxy[3]),
                        confidence=confidence,
                        label="hand",
                    )
                )
                confidences.append(confidence)

            if not confidences:
                return DetectionResult(0.0, [], True, "No detections")

            severity = float(sum(confidences) / len(confidences))
            return DetectionResult(severity, boxes, True, "Detections available")
        except Exception as exc:
            return DetectionResult(0.0, [], False, f"Inference error: {exc}")


class SprayController:
    def __init__(
        self, servos: ServoRig, detection_supplier: Callable[[], DetectionResult]
    ):
        self.servos = servos
        self._detection_supplier = detection_supplier
        self.paused = False
        self._spray_thread: threading.Thread | None = None
        self._spray_lock = threading.Lock()
        self._last_cycle_time = 0.0
        self.idle_scan_interval = 2.0

    def set_paused(self, paused: bool):
        self.paused = paused

    @property
    def is_paused(self) -> bool:
        return self.paused

    @property
    def is_spraying(self) -> bool:
        return self._spray_thread is not None and self._spray_thread.is_alive()

    def maybe_auto_spray(self):
        if self.paused or self.is_spraying:
            return

        detection = self._detection_supplier()
        if detection.severity > 0:
            self.start_spray_thread(detection.severity)
            return

        if time.monotonic() - self._last_cycle_time >= self.idle_scan_interval:
            self.start_spray_thread(0.0)

    def manual_spray(self):
        if self.is_spraying:
            return
        detection = self._detection_supplier()
        severity = max(detection.severity, 0.3)
        self.start_spray_thread(severity)

    def start_spray_thread(self, severity: float):
        with self._spray_lock:
            if self.is_spraying:
                return
            self._last_cycle_time = time.monotonic()
            self._spray_thread = threading.Thread(
                target=self.spray_sequence, args=(severity,), daemon=True
            )
            self._spray_thread.start()

    def sleep_or_pause(self, seconds: float):
        elapsed = 0.0
        while elapsed < seconds and not self.paused:
            interval = min(0.05, seconds - elapsed)
            time.sleep(interval)
            elapsed += interval

    def pump_for_severity(self, severity: float):
        if self.paused:
            return
        self.servos.set_pumps(True)
        self.sleep_or_pause(max(0.1, min(severity, 1.0) * MAX_SPRAY_TIME))
        self.servos.set_pumps(False)

    def spray_sequence(self, initial_severity: float):
        if self.paused:
            return

        def spray_if_needed(severity_hint: float | None = None) -> bool:
            if self.paused:
                return False
            detection = self._detection_supplier()
            severity = (
                detection.severity
                if severity_hint is None
                else max(detection.severity, severity_hint)
            )
            if severity <= 0:
                return False
            self.pump_for_severity(severity)
            return True

        if spray_if_needed(initial_severity):
            return

        self.servos.set_linkages(True)
        self.sleep_or_pause(self.servos.linkage_hold_time)
        if self.paused:
            self.servos.set_linkages(False)
            return

        if spray_if_needed():
            self.servos.set_linkages(False)
            return

        for interval in range(ARM_HEIGHT_INTERVALS):
            if self.paused:
                self.servos.set_linkages(False)
                return
            self.servos.set_arm_height((interval + 1) / ARM_HEIGHT_INTERVALS)
            if spray_if_needed():
                self.servos.set_linkages(False)
                return

        self.servos.set_linkages(False)


def draw_boxes(frame: np.ndarray, detection: DetectionResult) -> np.ndarray:
    output = frame.copy()
    for box in detection.boxes:
        cv2.rectangle(output, (box.x1, box.y1), (box.x2, box.y2), (0, 255, 0), 2)
        text = f"{box.label} {box.confidence:.2f}"
        cv2.putText(
            output,
            text,
            (box.x1, max(0, box.y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
    return output
