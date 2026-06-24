from dataclasses import dataclass
from re import S
from nicegui import ui

@dataclass
class Motor:
    enabled : bool
    min_speed : float
    max_speed : float
    pin : int
    left : bool    
    reversed : bool

class SettingsScreen:
    def __init__(self):
        self.motors : list[Motor] = [Motor(True, 0.4, 1.0, 8, True, False), Motor(True, 0.6, 1.0, 8, False, True)]
        
    def render(self):
        with ui.expansion("Capture"):
            with ui.card().classes("w-full"):
                ui.checkbox(text="enabled", value=True)            

                ui.label("FPS").classes("font-bold")
                ui.slider(min=1, max=60, value=30).props("label-always")

                ui.label("Sources").classes("font-bold")
                ui.input(label="forward", placeholder="0", value="0")
                ui.input(label="backward", placeholder="0", value="0")
                ui.input(label="arm", placeholder="0", value="0")

        with ui.expansion("YOLO"):
             with ui.card().classes("w-full"):
                ui.checkbox(text="enabled", value=True)                 
                ui.input(label="model path", placeholder="assets/main.pt", value="assets/main.pt")

                ui.label("Min Confidence").classes("font-bold")
                ui.slider(min=0, max=1, value=0.4, step=0.01).props("label-always")

        with ui.expansion("Motor"):
            with ui.card().classes("w-full"):
                ui.checkbox(text="enabled", value=True)

                ui.label("Motors").classes("font-bold")

                with ui.row():
                    for i, motor in enumerate(self.motors):
                        with ui.card():
                            with ui.row():
                                ui.label(text=str(i)).classes("font-extrabold")
                                ui.checkbox(text="enabled", value=motor.enabled)
                                ui.checkbox(text="is left", value=motor.left)
                                ui.checkbox(text="reversed", value=motor.reversed)

                            ui.number(label="pin", placeholder=0, value=motor.pin)
                            
                            ui.label("Min Speed").classes("font-bold")
                            ui.slider(min=-1, max=1, value=motor.min_speed, step=0.01).props("label-always")

                            ui.label("Max Speed").classes("font-bold")
                            ui.slider(min=-1, max=1, value=motor.max_speed, step=0.01).props("label-always") 
