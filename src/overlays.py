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
        on_manual_row_apply,
        on_manual_row_save_clamp,
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
        self.manual_row_apply = on_manual_row_apply
        self.manual_row_save_clamp = on_manual_row_save_clamp
        self.manual_rows: dict[str, dict[str, object]] = {}

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

        self.manual_rows_frame = ctk.CTkScrollableFrame(
            self.manual_panel, height=210, fg_color=ALTERNATE_DARK_COLOUR
        )
        self.manual_rows_frame.pack(fill="x", padx=8, pady=(0, PADDING_SMALL))

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

    def set_manual_targets(
        self,
        targets: list[str],
        saved_clamps: dict[str, tuple[bool, float, float]] | None = None,
    ):
        saved_clamps = saved_clamps or {}
        existing_state: dict[str, dict[str, str]] = {}
        for target, row in self.manual_rows.items():
            existing_state[target] = {
                "angle": row["angle_var"].get(),
                "clamp_enabled": "1" if row["clamp_enabled_var"].get() else "0",
                "clamp_min": row["clamp_min_var"].get(),
                "clamp_max": row["clamp_max_var"].get(),
            }

        for child in self.manual_rows_frame.winfo_children():
            child.destroy()
        self.manual_rows = {}

        full_targets = ["ALL"] + targets
        for target in full_targets:
            row = ctk.CTkFrame(self.manual_rows_frame, fg_color="transparent")
            row.pack(fill="x", padx=4, pady=2)
            top_row = ctk.CTkFrame(row, fg_color="transparent")
            top_row.pack(fill="x", pady=(0, 2))
            bottom_row = ctk.CTkFrame(row, fg_color="transparent")
            bottom_row.pack(fill="x", pady=(0, 2))
            clamp_row = ctk.CTkFrame(row, fg_color="transparent")
            clamp_row.pack(fill="x")
            action_row = ctk.CTkFrame(row, fg_color="transparent")
            action_row.pack(fill="x", pady=(2, 0))

            previous = existing_state.get(target, {})
            saved = saved_clamps.get(target)
            angle_var = ctk.StringVar(value=previous.get("angle", "0"))
            clamp_enabled_var = ctk.BooleanVar(
                value=(
                    previous.get("clamp_enabled", "0") == "1"
                    if previous
                    else (saved[0] if saved else False)
                )
            )
            clamp_min_var = ctk.StringVar(
                value=(
                    previous.get("clamp_min", "0")
                    if previous
                    else (str(saved[1]) if saved else "0")
                )
            )
            clamp_max_var = ctk.StringVar(
                value=(
                    previous.get("clamp_max", "360")
                    if previous
                    else (str(saved[2]) if saved else "360")
                )
            )

            ctk.CTkLabel(
                top_row, text=target, width=72, anchor="w", text_color=TEXT_COLOUR
            ).pack(side="left")

            slider_var = ctk.DoubleVar(value=float(angle_var.get() or 0))
            slider = ctk.CTkSlider(
                top_row,
                from_=0,
                to=360,
                width=1,
                variable=slider_var,
                fg_color=DEFAULT_COLOUR,
                progress_color=ACCENT_COLOUR,
                button_color=TEXT_COLOUR,
                button_hover_color=TEXT_COLOUR,
            )
            slider.pack(side="left", fill="x", expand=True, padx=(0, 4))

            ctk.CTkLabel(
                bottom_row, text="Angle", width=40, anchor="w", text_color=TEXT_COLOUR
            ).pack(side="left")
            angle_entry = ctk.CTkEntry(bottom_row, width=60, textvariable=angle_var)
            angle_entry.pack(side="left", padx=(0, 4))

            clamp_checkbox = ctk.CTkCheckBox(
                bottom_row,
                text="Clamp",
                width=24,
                variable=clamp_enabled_var,
                fg_color=DEFAULT_COLOUR,
                hover_color=TEXT_COLOUR,
            )
            clamp_checkbox.pack(side="left", padx=(0, 2))

            apply_button = ctk.CTkButton(
                action_row,
                text="Set",
                width=1,
                height=24,
                fg_color=ACCENT_COLOUR,
                text_color=DEFAULT_COLOUR,
            )
            apply_button.pack(side="left", fill="x", expand=True, padx=(0, 4))

            save_button = ctk.CTkButton(
                action_row,
                text="Save",
                width=1,
                height=24,
                fg_color=DEFAULT_COLOUR,
                hover_color=ACCENT_COLOUR,
                text_color=TEXT_COLOUR,
            )
            save_button.pack(side="left", fill="x", expand=True, padx=(4, 0))

            ctk.CTkLabel(
                clamp_row, text="Min", width=30, anchor="w", text_color=TEXT_COLOUR
            ).pack(side="left")
            clamp_min_entry = ctk.CTkEntry(
                clamp_row, width=64, textvariable=clamp_min_var
            )
            clamp_min_entry.pack(side="left", padx=(0, 8))
            ctk.CTkLabel(
                clamp_row, text="Max", width=30, anchor="w", text_color=TEXT_COLOUR
            ).pack(side="left")
            clamp_max_entry = ctk.CTkEntry(
                clamp_row, width=64, textvariable=clamp_max_var
            )
            clamp_max_entry.pack(side="left")

            self.manual_rows[target] = {
                "angle_var": angle_var,
                "slider_var": slider_var,
                "clamp_enabled_var": clamp_enabled_var,
                "clamp_min_var": clamp_min_var,
                "clamp_max_var": clamp_max_var,
                "slider": slider,
            }

            def apply_row(t=target):
                self.apply_manual_row(t)

            slider.configure(
                command=lambda value, t=target: self.on_slider_change(t, value)
            )
            angle_entry.bind("<Return>", lambda _e, t=target: self.apply_manual_row(t))
            angle_entry.bind(
                "<KeyRelease>", lambda _e, t=target: self.on_angle_entry_change(t)
            )
            clamp_checkbox.configure(command=apply_row)
            apply_button.configure(command=apply_row)
            save_button.configure(
                command=lambda t=target: self.save_manual_row_clamp(t)
            )

            self.update_row_slider_range(target)

    def toggle_manual_panel(self):
        self.manual_panel_open = not self.manual_panel_open
        if self.manual_panel_open:
            self.manual_panel.pack(fill="x", padx=10, pady=(0, PADDING_SMALL))
            self.manual_dropdown_button.configure(text="Manual Controls ▲")
        else:
            self.manual_panel.pack_forget()
            self.manual_dropdown_button.configure(text="Manual Controls ▼")

    def on_slider_change(self, target: str, value: float):
        row = self.manual_rows.get(target)
        if row is None:
            return
        row["angle_var"].set(f"{value:.1f}")
        self.apply_manual_row(target)

    def on_angle_entry_change(self, target: str):
        row = self.manual_rows.get(target)
        if row is None:
            return
        try:
            value = float(row["angle_var"].get())
        except ValueError:
            return
        slider = row["slider"]
        min_angle = float(slider.cget("from_"))
        max_angle = float(slider.cget("to"))
        value = max(min_angle, min(value, max_angle))
        row["slider_var"].set(value)

    def update_row_slider_range(self, target: str):
        row = self.manual_rows.get(target)
        if row is None:
            return
        slider = row["slider"]
        clamp_enabled = row["clamp_enabled_var"].get()
        if not clamp_enabled:
            slider.configure(from_=0, to=360)
            return
        try:
            clamp_min = float(row["clamp_min_var"].get())
            clamp_max = float(row["clamp_max_var"].get())
        except ValueError:
            slider.configure(from_=0, to=360)
            return
        if clamp_max < clamp_min:
            clamp_min, clamp_max = clamp_max, clamp_min
        slider.configure(from_=clamp_min, to=clamp_max)

    def apply_manual_row(self, target: str):
        row = self.manual_rows.get(target)
        if row is None:
            return
        self.update_row_slider_range(target)
        self.manual_row_apply(
            target,
            row["angle_var"].get(),
            row["clamp_enabled_var"].get(),
            row["clamp_min_var"].get(),
            row["clamp_max_var"].get(),
        )

    def save_manual_row_clamp(self, target: str):
        row = self.manual_rows.get(target)
        if row is None:
            return
        self.manual_row_save_clamp(
            target,
            row["clamp_enabled_var"].get(),
            row["clamp_min_var"].get(),
            row["clamp_max_var"].get(),
        )
