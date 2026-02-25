from dataclasses import dataclass, field
from pathlib import Path
import time
import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image
from config import Config
from constants import ALTERNATE_DARK_COLOUR, CONFIG_PATH, WINDOW_SIZE, UI_SCALE
from controllers import (
    CaptureManager,
    DetectionResult,
    ServoRig,
    SprayController,
    YoloDetector,
    draw_boxes,
)
from overlays import Overlay
from settings import SettingsPopUp


@dataclass
class Assets:
    arrow_up: ctk.CTkImage = field(
        default_factory=lambda: Assets.get_assets_path("arrow_up.png")
    )
    close: ctk.CTkImage = field(
        default_factory=lambda: Assets.get_assets_path("close.png")
    )
    pause: ctk.CTkImage = field(
        default_factory=lambda: Assets.get_assets_path("pause.png")
    )
    spray: ctk.CTkImage = field(
        default_factory=lambda: Assets.get_assets_path("spray.png")
    )
    settings: ctk.CTkImage = field(
        default_factory=lambda: Assets.get_assets_path("settings.png")
    )

    @classmethod
    def get_assets_path(cls, file: str = "") -> ctk.CTkImage:
        image = Image.open(f"{Path(__file__).parent}/assets/{file}")
        return ctk.CTkImage(light_image=image, dark_image=image, size=(15, 15))


class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=ALTERNATE_DARK_COLOUR)
        self.title("The Vermis App")
        self.geometry(f"{WINDOW_SIZE['x']}x{WINDOW_SIZE['y']}")
        try:
            self.state("zoomed")
        except Exception:
            pass
        ctk.DrawEngine.preferred_drawing_method = "circle_shapes"
        ctk.set_widget_scaling(UI_SCALE)
        ctk.set_appearance_mode("dark")

        self.assets = Assets()
        self.config = Config.load_from_file(CONFIG_PATH)
        self.width, self.height = (
            self.config.capture.resolution["x"],
            self.config.capture.resolution["y"],
        )

        self.capture_manager = CaptureManager(self.config.capture)
        self.yolo_detector = YoloDetector(self.config.yolo)
        self.servo_rig = ServoRig(self.config.servo_pins)

        self.last_detection = DetectionResult(0.0, [], False, "Waiting for frame")
        self.spray_controller = SprayController(self.servo_rig, self.get_last_detection)
        self.spray_controller.set_paused(True)
        self.arm_raise_stage = 0
        self.started_at = time.monotonic()
        self.manual_control_enabled = False

        self.video_widget = ctk.CTkLabel(self, text="")
        self.video_widget.pack(fill="both", expand=True)

        self.overlay = Overlay(
            self,
            on_pause=self.toggle_pause,
            on_spray=self.manual_spray,
            on_rise=self.raise_arm,
            on_manual_toggle=self.set_manual_control,
            on_manual_row_apply=self.apply_manual_row,
            on_manual_row_save_clamp=self.save_manual_row_clamp,
        )
        self.overlay.place(x=10, y=10)
        self.update_servo_status()
        self.overlay.set_manual_targets(
            self.servo_rig.manual_targets(), self.manual_clamp_map()
        )

        self.settings: SettingsPopUp | None = None

        self.bind("<Escape>", lambda _e: self.quit_app())
        self.protocol("WM_DELETE_WINDOW", self.quit_app)

        self.open_settings()
        self.start_camera()

    def get_last_detection(self) -> DetectionResult:
        return self.last_detection

    def apply_runtime_config(self, config: Config):
        self.config = config
        self.width = self.config.capture.resolution["x"]
        self.height = self.config.capture.resolution["y"]

        self.capture_manager.apply_config(self.config.capture)
        self.yolo_detector.apply_config(self.config.yolo)
        self.servo_rig.apply_config(self.config.servo_pins)
        self.overlay.set_manual_targets(
            self.servo_rig.manual_targets(), self.manual_clamp_map()
        )
        self.update_servo_status()

    def manual_clamp_map(self) -> dict[str, tuple[bool, float, float]]:
        mapping: dict[str, tuple[bool, float, float]] = {}
        for servo_cfg in self.config.servo_pins.servos:
            key = f"{servo_cfg.role}:{servo_cfg.pin}"
            mapping[key] = (
                bool(servo_cfg.clamp_enabled),
                float(servo_cfg.clamp_min_angle),
                float(servo_cfg.clamp_max_angle),
            )
        return mapping

    def update_servo_status(self):
        if self.servo_rig.total_channels == 0:
            self.overlay.set_servo_status("No channels configured")
            return
        self.overlay.set_servo_status(
            f"{self.servo_rig.available_channels}/{self.servo_rig.total_channels} active"
        )

    def start_camera(self):
        frame = self.capture_manager.read()

        if frame is None:
            display = self.blank_frame()
            self.last_detection = DetectionResult(
                0.0, [], False, "Capture disabled or unavailable"
            )
            self.overlay.set_capture_status("Disabled/Unavailable")
            self.overlay.set_yolo_status("Idle")
        else:
            self.overlay.set_capture_status("Running")
            detection = self.yolo_detector.detect(frame)
            self.last_detection = detection

            if detection.active and self.config.yolo.enabled:
                display = draw_boxes(frame, detection)
                self.overlay.set_yolo_status(
                    "Running"
                    if detection.reason == "Detections available"
                    else detection.reason
                )
            else:
                display = frame
                self.overlay.set_yolo_status(detection.reason or "Inactive")

            if not self.spray_controller.is_paused:
                self.spray_controller.maybe_auto_spray()

        self.overlay.set_confidence(self.last_detection.severity)
        self.overlay.set_stage(self.current_stage())
        self.overlay.set_paused_state(self.spray_controller.is_paused)
        self.overlay.set_uptime(self.format_uptime())
        self.overlay.set_battery(self.read_battery_status())
        self.overlay.set_distance("10km")

        self.update_idletasks()
        target_width = max(320, int(self.video_widget.winfo_width()))
        target_height = max(240, int(self.video_widget.winfo_height()))
        display = self.fit_frame_to_widget(display, target_width, target_height)

        opencv_image = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        captured_image = Image.fromarray(opencv_image)
        photo_image = ctk.CTkImage(
            light_image=captured_image,
            dark_image=captured_image,
            size=(
                max(1, int(target_width / UI_SCALE)),
                max(1, int(target_height / UI_SCALE)),
            ),
        )
        self.video_widget.configure(image=photo_image)
        self.video_widget.image = photo_image
        self.video_widget.after(self.frame_interval_ms(), self.start_camera)

    def frame_interval_ms(self) -> int:
        fps = max(1, int(self.config.capture.capture_fps))
        return max(1, int(1000 / fps))

    def fit_frame_to_widget(self, frame, target_width: int, target_height: int):
        frame_height, frame_width = frame.shape[:2]
        if frame_height <= 0 or frame_width <= 0:
            return cv2.resize(frame, (target_width, target_height))

        scale = min(target_width / frame_width, target_height / frame_height)
        new_width = max(1, int(frame_width * scale))
        new_height = max(1, int(frame_height * scale))

        resized = cv2.resize(frame, (new_width, new_height))
        canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)

        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        canvas[y_offset : y_offset + new_height, x_offset : x_offset + new_width] = (
            resized
        )
        return canvas

    def blank_frame(self):
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        cv2.putText(
            frame,
            "Capture disabled",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (200, 200, 200),
            2,
            cv2.LINE_AA,
        )
        return frame

    def current_stage(self) -> str:
        if self.spray_controller.is_paused:
            return "Paused"
        if self.spray_controller.is_spraying:
            return "Spraying"
        if self.last_detection.severity > 0:
            return "Target detected"
        return "Searching"

    def format_uptime(self) -> str:
        elapsed = int(max(0, time.monotonic() - self.started_at))
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def read_battery_status(self) -> str:
        try:
            import psutil

            battery = psutil.sensors_battery()
            if battery is None or battery.percent is None:
                return "N/A"
            return f"{int(battery.percent)}%"
        except Exception:
            return "N/A"

    def toggle_pause(self):
        if self.manual_control_enabled:
            return
        self.spray_controller.set_paused(not self.spray_controller.is_paused)

    def manual_spray(self):
        self.spray_controller.manual_spray()

    def raise_arm(self):
        if self.manual_control_enabled:
            return
        self.arm_raise_stage = (self.arm_raise_stage + 1) % 4
        self.servo_rig.set_arm_height(self.arm_raise_stage / 3, force=True)

    def set_manual_control(self, enabled: bool):
        self.manual_control_enabled = enabled
        self.spray_controller.set_paused(enabled)
        self.overlay.set_paused_state(self.spray_controller.is_paused)

    def apply_manual_row(
        self,
        target: str,
        angle_text: str,
        clamp_enabled: bool,
        min_text: str,
        max_text: str,
    ):
        if not self.manual_control_enabled:
            return
        try:
            angle = float(angle_text)
            clamp_min = float(min_text)
            clamp_max = float(max_text)
        except ValueError:
            return
        if clamp_max < clamp_min:
            clamp_min, clamp_max = clamp_max, clamp_min
        if clamp_enabled:
            angle = max(clamp_min, min(angle, clamp_max))

        if target == "ALL":
            for per_target in self.servo_rig.manual_targets():
                self.servo_rig.set_manual_angle(per_target, angle, force=True)
            return

        self.servo_rig.set_manual_angle(target, angle, force=True)

    def save_manual_row_clamp(
        self, target: str, clamp_enabled: bool, min_text: str, max_text: str
    ):
        try:
            clamp_min = float(min_text)
            clamp_max = float(max_text)
        except ValueError:
            return
        if clamp_max < clamp_min:
            clamp_min, clamp_max = clamp_max, clamp_min
        self.persist_clamp(target, clamp_enabled, clamp_min, clamp_max)

    def persist_clamp(
        self, target: str, clamp_enabled: bool, clamp_min: float, clamp_max: float
    ):
        changed = False

        def apply_to(role: str, pin: int):
            nonlocal changed
            for servo_cfg in self.config.servo_pins.servos:
                if servo_cfg.role == role and servo_cfg.pin == pin:
                    if (
                        bool(servo_cfg.clamp_enabled) != bool(clamp_enabled)
                        or float(servo_cfg.clamp_min_angle) != clamp_min
                        or float(servo_cfg.clamp_max_angle) != clamp_max
                    ):
                        servo_cfg.clamp_enabled = bool(clamp_enabled)
                        servo_cfg.clamp_min_angle = clamp_min
                        servo_cfg.clamp_max_angle = clamp_max
                        changed = True
                    break

        if target == "ALL":
            for t in self.servo_rig.manual_targets():
                role, pin_text = t.split(":", 1)
                apply_to(role, int(pin_text))
        else:
            role, pin_text = target.split(":", 1)
            apply_to(role, int(pin_text))

        if changed:
            self.config.save_to_file(CONFIG_PATH)
            self.servo_rig.apply_config(self.config.servo_pins)

    def open_settings(self):
        if self.settings is not None and self.settings.winfo_exists():
            self.settings.focus()
            return
        self.settings = SettingsPopUp(self)

    def quit_app(self):
        self.capture_manager.close()
        self.servo_rig.shutdown()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
