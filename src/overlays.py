from constants import *
from widgets import *
import customtkinter as ctk


class Overlay(ctk.CTkFrame):
    def __init__(
        self,
        master,
        on_pause,
        on_spray,
        on_rise,
        on_manual_toggle,
        on_manual_target,
        on_manual_angle,
        on_manual_clamp_toggle,
        **kwargs,
    ):
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

        manual_separator = Line(self, color=DEFAULT_COLOUR)
        manual_separator.pack(pady=PADDING_SMALL, fill="x", padx=10)

        self.manual_panel_open = False
        self.manual_enabled = ctk.BooleanVar(value=False)
        self.manual_target = ctk.StringVar(value="None")
        self.manual_angle = ctk.DoubleVar(value=0.0)
        self.manual_clamp_enabled = ctk.BooleanVar(value=False)
        self.manual_clamp_min = ctk.StringVar(value="0")
        self.manual_clamp_max = ctk.StringVar(value="360")

        self.manual_dropdown_button = ctk.CTkButton(
            self,
            text="Manual Controls ▼",
            command=self.toggle_manual_panel,
            height=26,
            fg_color=DEFAULT_COLOUR,
            hover_color=ACCENT_COLOUR,
            text_color=TEXT_COLOUR,
            anchor="w",
        )
        self.manual_dropdown_button.pack(fill="x", padx=10, pady=(0, PADDING_SMALL))

        self.manual_panel = ctk.CTkFrame(self, fg_color=DEFAULT_COLOUR)

        manual_toggle = NamedCheckbox(
            self.manual_panel,
            input_var=self.manual_enabled,
            label="Enable Manual Servo Control",
        )
        manual_toggle.checkbox.configure(
            command=lambda: on_manual_toggle(self.manual_enabled.get())
        )
        manual_toggle.pack(fill="x", padx=6, pady=(PADDING_SMALL, PADDING_SMALL))

        self.manual_target_dropdown = ctk.CTkOptionMenu(
            self.manual_panel,
            values=["None"],
            variable=self.manual_target,
            command=on_manual_target,
            height=26,
            fg_color=ALTERNATE_DARK_COLOUR,
            button_color=ACCENT_COLOUR,
            button_hover_color=ACCENT_COLOUR,
            text_color=TEXT_COLOUR,
        )
        self.manual_target_dropdown.pack(fill="x", padx=10, pady=(0, PADDING_SMALL))

        self.manual_angle_slider = NamedSlider(
            self.manual_panel,
            input_var=self.manual_angle,
            label="Manual Angle",
            from_=0,
            to=360,
        )
        self.manual_angle_slider.slider.configure(
            command=lambda _v: on_manual_angle(self.manual_angle.get())
        )
        self.manual_angle_slider.pack(fill="x", padx=6, pady=(0, PADDING_SMALL))

        clamp_toggle = NamedCheckbox(
            self.manual_panel,
            input_var=self.manual_clamp_enabled,
            label="Clamp Manual Range",
        )
        clamp_toggle.checkbox.configure(
            command=lambda: on_manual_clamp_toggle(
                self.manual_clamp_enabled.get(),
                self.manual_clamp_min.get(),
                self.manual_clamp_max.get(),
            )
        )
        clamp_toggle.pack(fill="x", padx=6, pady=(0, PADDING_SMALL))

        clamp_row = ctk.CTkFrame(self.manual_panel, fg_color="transparent")
        clamp_row.pack(fill="x", padx=6, pady=(0, PADDING_SMALL))
        clamp_min = NamedEntry(
            clamp_row, input_var=self.manual_clamp_min, label="Clamp Min"
        )
        clamp_min.pack(side="left", fill="x", expand=True, padx=(0, PADDING_SMALL))
        clamp_max = NamedEntry(
            clamp_row, input_var=self.manual_clamp_max, label="Clamp Max"
        )
        clamp_max.pack(side="left", fill="x", expand=True, padx=(PADDING_SMALL, 0))

        apply_clamp = ctk.CTkButton(
            self.manual_panel,
            text="Apply Clamp",
            command=lambda: on_manual_clamp_toggle(
                self.manual_clamp_enabled.get(),
                self.manual_clamp_min.get(),
                self.manual_clamp_max.get(),
            ),
            height=24,
            fg_color=ACCENT_COLOUR,
            text_color=DEFAULT_COLOUR,
        )
        apply_clamp.pack(fill="x", padx=10, pady=(0, PADDING_SMALL))

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

    def set_manual_targets(self, targets: list[str]):
        values = targets if targets else ["None"]
        self.manual_target_dropdown.configure(values=values)
        if self.manual_target.get() not in values:
            self.manual_target.set(values[0])

    def toggle_manual_panel(self):
        self.manual_panel_open = not self.manual_panel_open
        if self.manual_panel_open:
            self.manual_panel.pack(fill="x", padx=10, pady=(0, PADDING_SMALL))
            self.manual_dropdown_button.configure(text="Manual Controls ▲")
        else:
            self.manual_panel.pack_forget()
            self.manual_dropdown_button.configure(text="Manual Controls ▼")

    def set_manual_angle_range(self, min_angle: float, max_angle: float):
        self.manual_angle_slider.slider.configure(from_=min_angle, to=max_angle)
        clamped = max(min_angle, min(self.manual_angle.get(), max_angle))
        self.manual_angle.set(clamped)
