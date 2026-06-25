from nicegui import ui
from video import CV2Video
from config import Config
from controller.motor import MotorController
from controller.pump import PumpController
from controller.servo import ServoController
from controller.input import ControllerInput
from threading import Thread
import time


class ControlScreen:
    def __init__(self, config: Config):
        self.config = config
        self.video = CV2Video("main", config.capture.forward_source)

        self.motor_controller = (
            MotorController(config.motors) if config.motors_enabled else None
        )
        self.pump_controller = (
            PumpController(config.pumps) if config.pumps_enabled else None
        )
        self.servo_controller = (
            ServoController(config.servos) if config.servos_enabled else None
        )
        self.controller_input = ControllerInput()

        self.movement_forward = 0.0
        self.movement_turn = 0.0
        self.arm_base = 0.0
        self.arm_mid = 0.0
        self.arm_top = 0.0
        self.pump_forward = False
        self.use_controller = False

        self.controller_thread = None
        self.running = False

    def start_controller_thread(self):
        self.use_controller = True
        self.running = True
        self.controller_thread = Thread(target=self.handle_controller, daemon=True)
        self.controller_thread.start()

    def stop_controller_thread(self):
        self.use_controller = False
        self.running = False

    def on_mode_change(self, mode: str):
        if mode == "Controller":
            self.start_controller_thread()
        else:
            self.stop_controller_thread()

    def get_servo_config_by_type(self, servo_type: int):
        if not self.servo_controller:
            return None
        for config in self.config.servos:
            if config.type == servo_type:
                return config
        return None

    def handle_controller(self):
        try:
            for state in self.controller_input.get_controller_state():
                if not self.running:
                    break

                self.movement_forward = -state.left.y
                self.movement_turn = state.left.x

                base = self.get_servo_config_by_type(0)
                if base and base.continuous:
                    self.arm_base = state.right.x
                else:
                    self.arm_base = state.right.x * 180

                mid = self.get_servo_config_by_type(1)
                if mid and mid.continuous:
                    self.arm_mid = -state.right.y
                else:
                    self.arm_mid = -state.right.y * 90

                top = self.get_servo_config_by_type(2)
                if top and top.continuous:
                    self.arm_top = -state.right.y
                else:
                    self.arm_top = -state.right.y * 90

                self.pump_forward = state.a_button

                self.apply_controls()

                time.sleep(0.016)
        except Exception as e:
            print(f"Controller Error: {e}")

    def apply_controls(self):
        if self.motor_controller:
            self.motor_controller.set_tank_steering(
                self.movement_forward, self.movement_turn
            )

        if self.servo_controller:
            self.servo_controller.set_arm_angles(
                self.arm_base, self.arm_mid, self.arm_top
            )

        if self.pump_controller:
            if self.pump_forward:
                self.pump_controller.start()
            else:
                self.pump_controller.stop()

    def stop_all(self):
        self.running = False
        if self.motor_controller:
            self.motor_controller.stop()
        if self.pump_controller:
            self.pump_controller.stop()
        if self.servo_controller:
            self.servo_controller.stop()

    def cleanup(self):
        self.stop_all()
        if self.motor_controller:
            self.motor_controller.cleanup()
        if self.pump_controller:
            self.pump_controller.cleanup()
        if self.servo_controller:
            self.servo_controller.cleanup()

    def render(self):
        with ui.tabs().classes("w-full object-cover") as tabs:
            ui.tab("forward")
            ui.tab("backward")
            ui.tab("arm")

        with ui.tab_panels(tabs, value="forward").classes(
            "w-full object-cover h-[90vh]"
        ):
            with ui.tab_panel("forward"):
                self.video.change_source(self.config.capture.forward_source)
                self.video.render()
            with ui.tab_panel("backward"):
                self.video.change_source(self.config.capture.backward_source)
                self.video.render()
            with ui.tab_panel("arm"):
                self.video.change_source(self.config.capture.arm_source)
                self.video.render()

        with ui.card().classes(
            "absolute bottom-4 left-4 z-10 backdrop-blur-md bg-black/30 p-4 w-72 rounded-xl border border-white/20"
        ):
            with ui.expansion("Movement", icon="directions_car").classes(
                "w-full text-white"
            ):
                with ui.row().classes("justify-center mb-2"):
                    with ui.row().classes("justify-center mb-2"):
                        ui.icon("sym_o_mobiledata_arrows").classes("text-3xl")
                        ui.slider(min=-1, max=1, value=0, step=0.01).props(
                            "label-always vertical dark"
                        ).bind_value(self, "movement_forward").on(
                            "change", lambda: self.apply_controls()
                        )

                    with ui.row().classes("justify-center mb-2"):
                        ui.icon("sym_o_arrows_outward").classes("text-3xl")
                        ui.slider(min=-1, max=1, value=0, step=0.01).props(
                            "label-always vertical dark"
                        ).bind_value(self, "movement_turn").on(
                            "change", lambda: self.apply_controls()
                        )

            with ui.expansion("Arm", icon="precision_manufacturing").classes(
                "w-full text-white"
            ):
                base = self.get_servo_config_by_type(0)
                if base and base.continuous:
                    ui.label("Base (Speed)").classes("text-sm text-white")
                    ui.slider(min=-1, max=1, value=0, step=0.01).props(
                        "label-always dark"
                    ).bind_value(self, "arm_base").on(
                        "change", lambda: self.apply_controls()
                    )
                else:
                    ui.label("Base (Angle)").classes("text-sm text-white")
                    ui.slider(min=-180, max=180, value=0, step=1).props(
                        "label-always dark"
                    ).bind_value(self, "arm_base").on(
                        "change", lambda: self.apply_controls()
                    )

                mid = self.get_servo_config_by_type(1)
                if mid and mid.continuous:
                    ui.label("Mid (Speed)").classes("text-sm text-white")
                    ui.slider(min=-1, max=1, value=0, step=0.01).props(
                        "label-always dark"
                    ).bind_value(self, "arm_mid").on(
                        "change", lambda: self.apply_controls()
                    )
                else:
                    ui.label("Mid (Angle)").classes("text-sm text-white")
                    ui.slider(min=-90, max=90, value=0, step=1).props(
                        "label-always dark"
                    ).bind_value(self, "arm_mid").on(
                        "change", lambda: self.apply_controls()
                    )

                top = self.get_servo_config_by_type(2)
                if top and top.continuous:
                    ui.label("Top (Speed)").classes("text-sm text-white")
                    ui.slider(min=-1, max=1, value=0, step=0.01).props(
                        "label-always dark"
                    ).bind_value(self, "arm_top").on(
                        "change", lambda: self.apply_controls()
                    )
                else:
                    ui.label("Top (Angle)").classes("text-sm text-white")
                    ui.slider(min=-90, max=90, value=0, step=1).props(
                        "label-always dark"
                    ).bind_value(self, "arm_top").on(
                        "change", lambda: self.apply_controls()
                    )

            with ui.expansion("Pump", icon="water_drop").classes("w-full text-white"):
                ui.button(
                    "Pump",
                    on_click=lambda: (
                        setattr(self, "pump_forward", True),
                        self.apply_controls(),
                    ),
                ).classes("bg-blue-500 hover:bg-blue-600 text-white w-full").on(
                    "mouseup",
                    lambda: (
                        setattr(self, "pump_forward", False),
                        self.apply_controls(),
                    ),
                )

            with ui.expansion("System", icon="settings").classes("w-full text-white"):
                ui.button("Settings", on_click=lambda: ui.navigate.to("/")).classes(
                    "bg-blue-500 hover:bg-blue-600 text-white"
                )

                ui.label("Control Mode").classes("text-sm text-white mb-2")

                ui.toggle(
                    ["Manual", "Controller"],
                    value="Manual",
                    on_change=lambda e: self.on_mode_change(e.value),
                ).classes("text-white")
                
                ui.button("Stop All", on_click=self.stop_all).classes(
                    "bg-red-500 hover:bg-red-600 text-white w-full mt-2"
                )
