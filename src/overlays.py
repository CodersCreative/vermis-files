from constants import *
from widgets import *
import customtkinter as ctk


class Overlay(ctk.CTkFrame):
    def __init__(self, master, on_pause, on_spray, on_rise, **kwargs):
        super().__init__(master, fg_color=TEXT_COLOUR, **kwargs)
        row_frame = ctk.CTkFrame(self, fg_color="transparent")
        row_frame.pack(padx=10)

        quit_button = ctk.CTkButton(
            row_frame,
            text="",
            image=master.assets.close,
            width=18,
            command=master.quit_app,
            fg_color="transparent",
            text_color=DEFAULT_COLOUR,
            hover_color=ACCENT_COLOUR,
        )
        quit_button.pack(side="left", padx=(0, PADDING_SMALL))

        options = ctk.CTkButton(
            row_frame,
            text="",
            image=master.assets.settings,
            width=18,
            command=master.open_settings,
            fg_color="transparent",
            text_color=DEFAULT_COLOUR,
            hover_color=ACCENT_COLOUR,
        )
        options.pack(side="left", padx=PADDING_SMALL)

        self.pause_button = ctk.CTkButton(
            row_frame,
            text="",
            image=master.assets.pause,
            width=18,
            command=on_pause,
            fg_color="transparent",
            text_color=DEFAULT_COLOUR,
            hover_color=ACCENT_COLOUR,
        )
        self.pause_button.pack(side="left", padx=PADDING_SMALL)

        spray = ctk.CTkButton(
            row_frame,
            text="",
            image=master.assets.spray,
            width=18,
            command=on_spray,
            fg_color="transparent",
            text_color=DEFAULT_COLOUR,
            hover_color=ACCENT_COLOUR,
        )
        spray.pack(side="left", padx=PADDING_SMALL)

        rise = ctk.CTkButton(
            row_frame,
            text="",
            image=master.assets.arrow_up,
            width=18,
            command=on_rise,
            fg_color="transparent",
            text_color=DEFAULT_COLOUR,
            hover_color=ACCENT_COLOUR,
        )
        rise.pack(side="left", padx=(PADDING_SMALL, 0))

        buttons_separator = Line(self, color=DEFAULT_COLOUR)
        buttons_separator.pack(pady=PADDING_SMALL, fill="x", padx=10)

        self.confidence_label = ctk.CTkLabel(
            self, text="0%", font=MEDIUM_FONT, text_color=DEFAULT_COLOUR, anchor="w"
        )
        self.confidence_label.pack(fill="x", pady=0, ipady=0, padx=10)

        confidence_separator = Line(self, color=DEFAULT_COLOUR)
        confidence_separator.pack(pady=PADDING_SMALL, fill="x", padx=10)

        self.stage_label = ctk.CTkLabel(
            self,
            text="Stage: Idle",
            font=TINY_BOLD_FONT,
            text_color=DEFAULT_COLOUR,
            anchor="w",
        )
        self.stage_label.pack(fill="x", pady=0, padx=10)

        self.capture_label = ctk.CTkLabel(
            self,
            text="Capture: Ready",
            font=TINY_BOLD_FONT,
            text_color=DEFAULT_COLOUR,
            anchor="w",
        )
        self.capture_label.pack(fill="x", pady=0, padx=10)

        self.yolo_label = ctk.CTkLabel(
            self,
            text="YOLO: Ready",
            font=TINY_BOLD_FONT,
            text_color=DEFAULT_COLOUR,
            anchor="w",
        )
        self.yolo_label.pack(fill="x", pady=0, padx=10)

        self.servo_label = ctk.CTkLabel(
            self,
            text="Servos: Ready",
            font=TINY_BOLD_FONT,
            text_color=DEFAULT_COLOUR,
            anchor="w",
        )
        self.servo_label.pack(fill="x", pady=0, padx=10)

        self.uptime_label = ctk.CTkLabel(
            self,
            text="Uptime: 00:00:00",
            font=TINY_BOLD_FONT,
            text_color=DEFAULT_COLOUR,
            anchor="w",
        )
        self.uptime_label.pack(fill="x", pady=0, padx=10)

        self.battery_label = ctk.CTkLabel(
            self,
            text="Battery: N/A",
            font=TINY_BOLD_FONT,
            text_color=DEFAULT_COLOUR,
            anchor="w",
        )
        self.battery_label.pack(fill="x", pady=0, padx=10)

        self.distance_label = ctk.CTkLabel(
            self,
            text="Distance: 10km",
            font=TINY_BOLD_FONT,
            text_color=DEFAULT_COLOUR,
            anchor="w",
        )
        self.distance_label.pack(fill="x", pady=0, padx=10)

    def set_confidence(self, confidence: float):
        percentage = max(0.0, min(confidence, 1.0)) * 100
        self.confidence_label.configure(text=f"{percentage:.1f}%")

    def set_stage(self, stage: str):
        self.stage_label.configure(text=f"Stage: {stage}")

    def set_capture_status(self, status: str):
        self.capture_label.configure(text=f"Capture: {status}")

    def set_yolo_status(self, status: str):
        self.yolo_label.configure(text=f"YOLO: {status}")

    def set_servo_status(self, status: str):
        self.servo_label.configure(text=f"Servos: {status}")

    def set_uptime(self, uptime: str):
        self.uptime_label.configure(text=f"Uptime: {uptime}")

    def set_battery(self, battery: str):
        self.battery_label.configure(text=f"Battery: {battery}")

    def set_distance(self, distance: str):
        self.distance_label.configure(text=f"Distance: {distance}")

    def set_paused_state(self, paused: bool):
        color = DANGER_COLOUR if paused else "transparent"
        self.pause_button.configure(fg_color=color)
