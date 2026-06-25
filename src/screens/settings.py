from nicegui import ui
from config import Config, ServoType


class SettingsScreen:
    def __init__(self):
        self.config = Config.load_from_file()

    def save_config(self):
        self.config.save_to_file()

    def render(self):
        with ui.card().classes("w-full p-2 mb-4"):
            with ui.row().classes("justify-between items-center w-full"):
                ui.label("Settings").classes("font-bold text-xl")
                ui.button(
                    "Start", on_click=lambda: ui.navigate.to("/control/")
                ).classes("bg-blue-500 hover:bg-blue-600 text-white")

        with ui.expansion("Capture").classes("w-full"):
            with ui.card().classes("w-full"):
                ui.checkbox(
                    text="enabled", value=self.config.capture.enabled
                ).bind_value(self.config.capture, "enabled")

                ui.label("FPS").classes("font-bold")
                ui.slider(min=1, max=60, value=self.config.capture.fps).props(
                    "label-always"
                ).bind_value(self.config.capture, "fps")

                ui.label("Sources").classes("font-bold")
                ui.input(
                    label="forward",
                    placeholder="0",
                    value=str(self.config.capture.forward_source),
                ).bind_value(self.config.capture, "forward_source")
                ui.input(
                    label="backward",
                    placeholder="0",
                    value=str(self.config.capture.backward_source),
                ).bind_value(self.config.capture, "backward_source")
                ui.input(
                    label="arm",
                    placeholder="0",
                    value=str(self.config.capture.arm_source),
                ).bind_value(self.config.capture, "arm_source")

        with ui.expansion("YOLO").classes("w-full"):
            with ui.card().classes("w-full"):
                ui.checkbox(text="enabled", value=self.config.yolo.enabled).bind_value(
                    self.config.yolo, "enabled"
                )

                ui.input(
                    label="model path",
                    placeholder="assets/main.pt",
                    value=self.config.yolo.model_path,
                ).bind_value(self.config.yolo, "model_path")

                ui.label("Min Confidence").classes("font-bold")
                ui.slider(
                    min=0, max=1, value=self.config.yolo.min_confidence, step=0.01
                ).props("label-always").bind_value(self.config.yolo, "min_confidence")

        with ui.expansion("Motors").classes("w-full"):
            with ui.card().classes("w-full"):
                ui.checkbox(
                    text="enabled", value=self.config.motors_enabled
                ).bind_value(self.config, "motors_enabled")

                ui.label("Motors").classes("font-bold")

                with ui.row():
                    for i, motor in enumerate(self.config.motors):
                        with ui.card():
                            with ui.row().classes("justify-center"):
                                ui.label(text=str(i)).classes("font-extrabold")
                                ui.checkbox(
                                    text="enabled", value=motor.enabled
                                ).bind_value(motor, "enabled")
                                ui.checkbox(
                                    text="is left", value=motor.left
                                ).bind_value(motor, "left")
                                ui.checkbox(
                                    text="reversed", value=motor.reversed
                                ).bind_value(motor, "reversed")

                            ui.number(
                                label="pin", placeholder=0, value=motor.pin
                            ).bind_value(motor, "pin")

                            ui.label("Min Speed").classes("font-bold")
                            ui.slider(
                                min=-1, max=1, value=motor.min_speed, step=0.01
                            ).props("label-always").bind_value(motor, "min_speed")

                            ui.label("Max Speed").classes("font-bold")
                            ui.slider(
                                min=-1, max=1, value=motor.max_speed, step=0.01
                            ).props("label-always").bind_value(motor, "max_speed")

        with ui.expansion("Pumps").classes("w-full"):
            with ui.card().classes("w-full"):
                ui.checkbox(
                    text="enabled", value=self.config.motors_enabled
                ).bind_value(self.config, "pumps_enabled")

                ui.label("Pumps").classes("font-bold")

                with ui.row():
                    for i, pump in enumerate(self.config.pumps):
                        with ui.card():
                            with ui.row().classes("justify-center"):
                                ui.label(text=str(i)).classes("font-extrabold")
                                ui.checkbox(
                                    text="enabled", value=pump.enabled
                                ).bind_value(pump, "enabled")

                            ui.number(
                                label="enable pin", placeholder=0, value=pump.enable_pin
                            ).bind_value(pump, "enable_pin")

                            ui.number(
                                label="forward pin",
                                placeholder=0,
                                value=pump.forward_pin,
                            ).bind_value(pump, "forward_pin")

                            ui.number(
                                label="backward pin",
                                placeholder=0,
                                value=pump.backward_pin,
                            ).bind_value(pump, "backward_pin")

        with ui.expansion("Servos").classes("w-full"):
            with ui.card().classes("w-full"):
                ui.checkbox(
                    text="enabled", value=self.config.servos_enabled
                ).bind_value(self.config, "servos_enabled")

                ui.label("Servos").classes("font-bold")

                with ui.row():
                    for i, servo in enumerate(self.config.servos):
                        with ui.card():
                            with ui.row().classes("justify-center"):
                                ui.label(text=str(i)).classes("font-extrabold")
                                ui.checkbox(
                                    text="enabled", value=servo.enabled
                                ).bind_value(servo, "enabled")

                            ui.number(
                                label="pin", placeholder=0, value=servo.pin
                            ).bind_value(servo, "pin")

                            ui.select(
                                {
                                    ServoType.BASE_ARM.value: "Base Arm",
                                    ServoType.MID_ARM.value: "Mid Arm",
                                    ServoType.TOP_ARM.value: "Top Arm",
                                },
                                value=servo.type,
                            ).bind_value(servo, "type")

                            ui.number(
                                label="Deadband",
                                placeholder=0,
                                value=servo.deadband,
                                precision=2,
                                step=0.01,
                            ).bind_value(servo, "deadband")
                            ui.number(
                                label="Interval",
                                placeholder=0,
                                value=servo.interval,
                                precision=2,
                                step=0.01,
                            ).bind_value(servo, "interval")

                            ui.label("Min Angle").classes("font-bold")
                            ui.slider(
                                min=-360, max=360, value=servo.min_angle, step=0.1
                            ).props("label-always").bind_value(servo, "min_angle")

                            ui.label("Max Angle").classes("font-bold")
                            ui.slider(
                                min=-360, max=360, value=servo.max_angle, step=0.1
                            ).props("label-always").bind_value(servo, "max_angle")

                            ui.label("Offset").classes("font-bold")
                            ui.slider(
                                min=-360, max=360, value=servo.offset, step=0.1
                            ).props("label-always").bind_value(servo, "offset")

        with ui.row():
            ui.button("save", on_click=self.save_config)
