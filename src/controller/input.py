from dataclasses import dataclass, field
from collections.abc import Iterator

try:
    from inputs import get_gamepad

    INPUTS_AVAILABLE = True
except ImportError:
    INPUTS_AVAILABLE = False


@dataclass
class Vector2:
    x: float = 0
    y: float = 0


@dataclass
class ControllerState:
    left: Vector2 = field(default_factory=lambda: Vector2())
    right: Vector2 = field(default_factory=lambda: Vector2())
    a_button: bool = False
    b_button: bool = False
    x_button: bool = False
    y_button: bool = False

    lb_button: bool = False
    rb_button: bool = False


class ControllerInput:
    def __init__(self):
        self.state = ControllerState()
        self.MAX_VAL = 32767

        if not INPUTS_AVAILABLE:
            print("inputs not available, controller input disabled")

    def get_controller_state(self) -> Iterator[ControllerState]:
        if not INPUTS_AVAILABLE:
            while True:
                yield self.state

        while True:
            events = get_gamepad()
            for event in events:
                self.handle_event(event)
            yield self.state

    def handle_event(self, event):
        code = event.code
        state = event.state

        if code == "ABS_X":
            self.state.left.x = round(state / self.MAX_VAL, 2)
        elif code == "ABS_Y":
            self.state.left.y = round(state / self.MAX_VAL, 2)

        elif code == "ABS_RX":
            self.state.right.x = round(state / self.MAX_VAL, 2)
        elif code == "ABS_RY":
            self.state.right.y = round(state / self.MAX_VAL, 2)

        elif code == "BTN_SOUTH":
            self.state.a_button = state == 1
        elif code == "BTN_EAST":
            self.state.b_button = state == 1
        elif code == "BTN_NORTH":
            self.state.x_button = state == 1
        elif code == "BTN_WEST":
            self.state.y_button = state == 1
        elif code == "BTN_TL":
            self.state.lb_button = state == 1
        elif code == "BTN_TR":
            self.state.rb_button = state == 1

    def get_movement_vector(self) -> Vector2:
        return Vector2(self.state.left.x, self.state.left.y)

    def get_arm_vector(self) -> Vector2:
        return Vector2(self.state.right.x, self.state.right.y)

    def get_pump_control(self) -> bool:
        return self.state.a_button
