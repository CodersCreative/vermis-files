from dataclasses import dataclass
from re import S
from nicegui import ui

@dataclass
class Motor:
    enabled : bool
    pin : int    
    min_speed : float
    max_speed : float
    left : bool    
    reversed : bool

@dataclass
class Servo:
    enabled : bool
    pin : int
    type : int
    min_angle : float
    max_angle : float
    offset : float    
    deadband : float
    interval : float

class SettingsScreen:
    def __init__(self):
        self.motors : list[Motor] = [Motor(True, 8, 0.4, 1.0, True, False), Motor(True, 10, 0.6, 1.0, False, True)]
        self.servos : list[Servo] = [Servo(True, 8, 0, 0, 360, 0, 1.5, 0.08), Servo(True, 10, 1, 0, 270, 0, 1.5, 0.1)]
        
    def render(self):
        with ui.expansion("Capture").classes("w-full"):
            with ui.card().classes("w-full"):
                ui.checkbox(text="enabled", value=True)            

                ui.label("FPS").classes("font-bold")
                ui.slider(min=1, max=60, value=30).props("label-always")

                ui.label("Sources").classes("font-bold")
                ui.input(label="forward", placeholder="0", value="0")
                ui.input(label="backward", placeholder="0", value="0")
                ui.input(label="arm", placeholder="0", value="0")

        with ui.expansion("YOLO").classes("w-full"):
             with ui.card().classes("w-full"):
                ui.checkbox(text="enabled", value=True)                 
                ui.input(label="model path", placeholder="assets/main.pt", value="assets/main.pt")

                ui.label("Min Confidence").classes("font-bold")
                ui.slider(min=0, max=1, value=0.4, step=0.01).props("label-always")

        with ui.expansion("Motors").classes("w-full"):
            with ui.card().classes("w-full"):
                ui.checkbox(text="enabled", value=True)

                ui.label("Motors").classes("font-bold")

                with ui.row():
                    for i, motor in enumerate(self.motors):
                        with ui.card():
                            with ui.row().classes('justify-center'):
                                ui.label(text=str(i)).classes("font-extrabold")
                                ui.checkbox(text="enabled", value=motor.enabled)
                                ui.checkbox(text="is left", value=motor.left)
                                ui.checkbox(text="reversed", value=motor.reversed)

                            ui.number(label="pin", placeholder=0, value=motor.pin)
                            
                            ui.label("Min Speed").classes("font-bold")
                            ui.slider(min=-1, max=1, value=motor.min_speed, step=0.01).props("label-always")

                            ui.label("Max Speed").classes("font-bold")
                            ui.slider(min=-1, max=1, value=motor.max_speed, step=0.01).props("label-always")


        with ui.expansion("Servos").classes("w-full"):
            with ui.card().classes("w-full"):
                ui.checkbox(text="enabled", value=True)
                
                ui.label("Servos").classes("font-bold")

                with ui.row():
                    for i, servo in enumerate(self.servos):
                        with ui.card():
                            with ui.row().classes('justify-center'):
                                ui.label(text=str(i)).classes("font-extrabold")
                                ui.checkbox(text="enabled", value=servo.enabled)

                            ui.number(label="pin", placeholder=0, value=servo.pin)
                            
                            ui.select({0 : "Pump", 1 : "Base Arm", 2 : "Top Arm"}, value=servo.type)

                            ui.number(label="Deadband", placeholder=0, value=servo.deadband, precision=2, step=0.01)
                            ui.number(label="Interval", placeholder=0, value=servo.interval, precision=2, step=0.01)                            
                            
                            ui.label("Min Angle").classes("font-bold")
                            ui.slider(min=-360, max=360, value=servo.min_angle, step=0.1).props("label-always")

                            ui.label("Max Angle").classes("font-bold")
                            ui.slider(min=-360, max=360, value=servo.max_angle, step=0.1).props("label-always") 

                            ui.label("Offset").classes("font-bold")
                            ui.slider(min=-360, max=360, value=servo.offset, step=0.1).props("label-always")

        with ui.row():
            ui.button("start");            
            ui.checkbox(text="save", value=servo.enabled)
            
