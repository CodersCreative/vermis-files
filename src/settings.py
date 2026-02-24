import customtkinter as ctk
from config import ServoPinConfig
from constants import *
from widgets import *


class SettingsPopUp(ctk.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=ALTERNATE_DARK_COLOUR, **kwargs)
        self.title("Vermis Settings")
        self.geometry("1280x720")

        self.linkage_hold_time = ctk.DoubleVar(
            value=master.config.servo_pins.linkage_hold_time
        )
        self.default_min_angle = ctk.DoubleVar(
            value=master.config.servo_pins.defaults.min_angle
        )
        self.default_max_angle = ctk.DoubleVar(
            value=master.config.servo_pins.defaults.max_angle
        )
        self.default_deadband = ctk.DoubleVar(
            value=master.config.servo_pins.defaults.deadband_degrees
        )
        self.default_command_interval = ctk.DoubleVar(
            value=master.config.servo_pins.defaults.command_interval_seconds
        )
        self.default_angle_offset = ctk.DoubleVar(
            value=master.config.servo_pins.defaults.angle_offset
        )

        self.resolution_x = ctk.IntVar(value=master.config.capture.resolution["x"])
        self.resolution_y = ctk.IntVar(value=master.config.capture.resolution["y"])
        self.capture_fps = ctk.IntVar(value=master.config.capture.capture_fps)
        self.ip_address = ctk.StringVar(value=master.config.capture.ip_address)
        self.use_webcam = ctk.BooleanVar(value=master.config.capture.use_webcam)
        self.capture_enabled = ctk.BooleanVar(value=master.config.capture.enabled)

        self.min_confidence = ctk.DoubleVar(value=master.config.yolo.min_confidence)
        self.yolo_path = ctk.StringVar(
            value=master.config.yolo.path or "assets/main.pt"
        )
        self.yolo_enabled = ctk.BooleanVar(value=master.config.yolo.enabled)

        self.status_text = ctk.StringVar(value="")
        self.master = master

        self.servo_rows: list[dict[str, object]] = []

        self.scroll_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        self.scroll_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.build_servo_settings(self.scroll_container)
        self.build_capture_settings(self.scroll_container)
        self.build_yolo_settings(self.scroll_container)

        save = ctk.CTkButton(
            self.scroll_container,
            text="Save",
            command=self.save_settings,
            text_color=DEFAULT_COLOUR,
            fg_color=ACCENT_COLOUR,
        )
        save.pack(pady=PADDING_SMALL, padx=PADDING_SMALL, fill="x")

        status = ctk.CTkLabel(
            self.scroll_container,
            textvariable=self.status_text,
            font=TINY_BOLD_FONT,
            text_color=TEXT_COLOUR,
            anchor="w",
        )
        status.pack(fill="x", padx=PADDING_SMALL)

    def build_servo_settings(self, container):
        servo_label = ctk.CTkLabel(container, text="Servo Settings", font=SMALL_FONT)
        servo_label.pack(pady=PADDING_SMALL)
        separator = Line(container)
        separator.pack(pady=PADDING_SMALL, fill="x")

        linkage_hold_time = NamedSlider(
            container,
            label="Linkage Hold Time",
            input_var=self.linkage_hold_time,
            from_=0,
            to=5,
        )
        linkage_hold_time.pack(pady=PADDING_SMALL, fill="x")

        row = ctk.CTkFrame(container, fg_color="transparent")
        row.pack(fill="x")
        default_min_angle = NamedEntry(
            row, input_var=self.default_min_angle, label="Default Min Angle"
        )
        default_min_angle.pack(
            side="left",
            pady=PADDING_SMALL,
            fill="x",
            expand=True,
            padx=(0, PADDING_SMALL),
        )
        default_max_angle = NamedEntry(
            row, input_var=self.default_max_angle, label="Default Max Angle"
        )
        default_max_angle.pack(
            side="left",
            pady=PADDING_SMALL,
            fill="x",
            expand=True,
            padx=(PADDING_SMALL, 0),
        )

        row = ctk.CTkFrame(container, fg_color="transparent")
        row.pack(fill="x")
        default_deadband = NamedEntry(
            row, input_var=self.default_deadband, label="Default Deadband"
        )
        default_deadband.pack(
            side="left",
            pady=PADDING_SMALL,
            fill="x",
            expand=True,
            padx=(0, PADDING_SMALL),
        )
        default_command_interval = NamedEntry(
            row,
            input_var=self.default_command_interval,
            label="Default Cmd Interval (s)",
        )
        default_command_interval.pack(
            side="left",
            pady=PADDING_SMALL,
            fill="x",
            expand=True,
            padx=(PADDING_SMALL, 0),
        )

        default_offset = NamedEntry(
            container, input_var=self.default_angle_offset, label="Default Angle Offset"
        )
        default_offset.pack(pady=PADDING_SMALL, fill="x")

        table_header = ctk.CTkFrame(container, fg_color="transparent")
        table_header.pack(fill="x", pady=(PADDING_SMALL, 0))
        for text, width in [
            ("Type", 65),
            ("Pin", 55),
            ("Offset", 80),
            ("Min", 70),
            ("Max", 70),
            ("Deadband", 85),
            ("Interval", 90),
            ("Edit", 56),
        ]:
            ctk.CTkLabel(
                table_header,
                text=text,
                width=width,
                anchor="w",
                font=TINY_BOLD_FONT,
                fg_color=DEFAULT_COLOUR,
                text_color=TEXT_COLOUR,
            ).pack(side="left")

        self.table_frame = ctk.CTkScrollableFrame(
            container, height=190, fg_color=DEFAULT_COLOUR
        )
        self.table_frame.pack(fill="x", pady=(0, PADDING_SMALL))

        controls = ctk.CTkFrame(container, fg_color="transparent")
        controls.pack(fill="x", pady=(0, PADDING_SMALL))

        add_row = ctk.CTkButton(
            controls,
            text="Add Servo Row",
            command=lambda: self.add_servo_row(ServoPinConfig(role="Link", pin=0)),
            text_color=DEFAULT_COLOUR,
            fg_color=ACCENT_COLOUR,
            height=26,
        )
        add_row.pack(side="left", fill="x", expand=True)

        self.load_servo_rows_from_config()

    def load_servo_rows_from_config(self):
        for servo_cfg in self.master.config.servo_pins.servos:
            self.add_servo_row(servo_cfg)

    def add_servo_row(self, servo_cfg: ServoPinConfig):
        row = ctk.CTkFrame(self.table_frame, fg_color="transparent")
        row.pack(fill="x", pady=1)

        role_var = ctk.StringVar(value=servo_cfg.role)
        pin_var = ctk.StringVar(value=str(servo_cfg.pin))
        offset_var = ctk.DoubleVar(value=float(servo_cfg.angle_offset))
        min_var = ctk.DoubleVar(value=float(servo_cfg.min_angle))
        max_var = ctk.DoubleVar(value=float(servo_cfg.max_angle))
        deadband_var = ctk.DoubleVar(value=float(servo_cfg.deadband_degrees))
        interval_var = ctk.DoubleVar(value=float(servo_cfg.command_interval_seconds))

        ctk.CTkOptionMenu(
            row,
            values=["Link", "Arm", "Pump"],
            variable=role_var,
            width=65,
            height=24,
        ).pack(side="left")
        ctk.CTkEntry(row, textvariable=pin_var, width=55, height=24).pack(
            side="left", padx=(4, 4)
        )
        ctk.CTkEntry(row, textvariable=offset_var, width=80, height=24).pack(
            side="left", padx=(0, 4)
        )
        ctk.CTkEntry(row, textvariable=min_var, width=70, height=24).pack(
            side="left", padx=(0, 4)
        )
        ctk.CTkEntry(row, textvariable=max_var, width=70, height=24).pack(
            side="left", padx=(0, 4)
        )
        ctk.CTkEntry(row, textvariable=deadband_var, width=85, height=24).pack(
            side="left", padx=(0, 4)
        )
        ctk.CTkEntry(row, textvariable=interval_var, width=90, height=24).pack(
            side="left", padx=(0, 4)
        )

        row_data: dict[str, object] = {
            "frame": row,
            "role": role_var,
            "pin": pin_var,
            "offset": offset_var,
            "min": min_var,
            "max": max_var,
            "deadband": deadband_var,
            "interval": interval_var,
        }

        ctk.CTkButton(
            row,
            text="-",
            width=24,
            height=24,
            fg_color=DANGER_COLOUR,
            text_color=DEFAULT_COLOUR,
            command=lambda r=row_data: self.remove_servo_row(r),
        ).pack(side="left")

        self.servo_rows.append(row_data)

    def remove_servo_row(self, row_data: dict[str, object]):
        frame = row_data["frame"]
        if isinstance(frame, ctk.CTkFrame):
            frame.destroy()
        self.servo_rows = [row for row in self.servo_rows if row is not row_data]

    def collect_table_rows(self) -> list[ServoPinConfig]:
        if not self.servo_rows:
            raise ValueError("Servo table cannot be empty")

        seen_pins: set[int] = set()
        servos: list[ServoPinConfig] = []

        for row in self.servo_rows:
            role = str(row["role"].get()).strip()
            pin_text = str(row["pin"].get()).strip()
            if not pin_text.isdigit():
                raise ValueError(f"Invalid pin '{pin_text}' in table")
            pin = int(pin_text)
            if pin in seen_pins:
                raise ValueError(f"Duplicate pin '{pin}' in table")
            seen_pins.add(pin)

            if role not in {"Link", "Arm", "Pump"}:
                raise ValueError(f"Invalid servo type '{role}'")

            try:
                servos.append(
                    ServoPinConfig(
                        role=role,
                        pin=pin,
                        angle_offset=float(row["offset"].get()),
                        min_angle=float(row["min"].get()),
                        max_angle=float(row["max"].get()),
                        deadband_degrees=max(0.0, float(row["deadband"].get())),
                        command_interval_seconds=max(0.0, float(row["interval"].get())),
                    )
                )
            except ValueError as exc:
                raise ValueError(f"Invalid numeric value for pin {pin}") from exc

        return servos

    def build_capture_settings(self, container):
        capture_label = ctk.CTkLabel(
            container, text="Capture Settings", font=SMALL_FONT
        )
        capture_label.pack(pady=PADDING_SMALL, fill="x")
        separator = Line(container)
        separator.pack(pady=PADDING_SMALL, fill="x")

        row_frame = ctk.CTkFrame(container, fg_color="transparent")
        row_frame.pack(fill="x")

        capture_enabled = NamedCheckbox(
            row_frame, input_var=self.capture_enabled, label="Enabled"
        )
        capture_enabled.pack(
            side="left",
            pady=PADDING_SMALL,
            padx=(0, PADDING_SMALL),
        )

        use_webcam = NamedCheckbox(
            row_frame, input_var=self.use_webcam, label="Use Webcam"
        )
        use_webcam.pack(side="left", pady=PADDING_SMALL, padx=(PADDING_SMALL, 0))

        row_frame = ctk.CTkFrame(container, fg_color="transparent")
        row_frame.pack(fill="x")

        resolution_x = NamedEntry(
            row_frame, input_var=self.resolution_x, label="X Resolution"
        )
        resolution_x.pack(
            side="left", pady=PADDING_SMALL, fill="x", padx=(0, PADDING_SMALL)
        )

        resolution_y = NamedEntry(
            row_frame, input_var=self.resolution_y, label="Y Resolution"
        )
        resolution_y.pack(
            side="left", pady=PADDING_SMALL, fill="x", padx=(PADDING_SMALL, 0)
        )

        capture_fps = NamedSlider(
            container,
            label="Capture FPS",
            input_var=self.capture_fps,
            from_=1,
            to=120,
        )
        capture_fps.pack(pady=PADDING_SMALL, fill="x")

        ip_address = NamedEntry(
            container, input_var=self.ip_address, label="IP Address"
        )
        ip_address.pack(pady=PADDING_SMALL, fill="x")

    def build_yolo_settings(self, container):
        yolo_label = ctk.CTkLabel(container, text="YOLO Settings", font=SMALL_FONT)
        yolo_label.pack(pady=PADDING_SMALL, fill="x")

        separator = Line(container)
        separator.pack(pady=PADDING_SMALL, fill="x")

        yolo_enabled = NamedCheckbox(
            container, input_var=self.yolo_enabled, label="Enabled"
        )
        yolo_enabled.pack(pady=PADDING_SMALL, fill="x")

        min_confidence = NamedSlider(
            container,
            label="Min Confidence",
            input_var=self.min_confidence,
            from_=0,
            to=1,
        )
        min_confidence.pack(pady=PADDING_SMALL, fill="x")

        yolo_path = NamedEntry(container, input_var=self.yolo_path, label="Model Path")
        yolo_path.pack(pady=PADDING_SMALL, fill="x")

    def save_settings(self):
        try:
            servo_entries = self.collect_table_rows()
        except ValueError as exc:
            self.status_text.set(f"Validation error: {exc}")
            return

        config = self.master.config
        config.servo_pins.linkage_hold_time = self.linkage_hold_time.get()
        config.servo_pins.defaults = ServoPinConfig(
            role="Default",
            pin=0,
            angle_offset=self.default_angle_offset.get(),
            min_angle=self.default_min_angle.get(),
            max_angle=self.default_max_angle.get(),
            deadband_degrees=max(0.0, self.default_deadband.get()),
            command_interval_seconds=max(0.0, self.default_command_interval.get()),
        )
        config.servo_pins.servos = servo_entries

        config.capture.enabled = self.capture_enabled.get()
        config.capture.ip_address = self.ip_address.get().strip()
        config.capture.resolution["x"] = max(160, self.resolution_x.get())
        config.capture.resolution["y"] = max(120, self.resolution_y.get())
        config.capture.capture_fps = max(1, min(120, int(self.capture_fps.get())))
        config.capture.use_webcam = self.use_webcam.get()

        config.yolo.enabled = self.yolo_enabled.get()
        config.yolo.min_confidence = min(1.0, max(0.0, self.min_confidence.get()))
        config.yolo.path = self.yolo_path.get().strip()

        self.master.apply_runtime_config(config)
        config.save_to_file(CONFIG_PATH)
        self.status_text.set("Settings applied")
