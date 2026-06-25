import time
from dataclasses import dataclass
from config import MotorConfig

try:
    from gpiozero import PWMOutputDevice
    from gpiozero.pins.lgpio import LGPIOFactory

    GPIOZERO_AVAILABLE = True
except ImportError:
    GPIOZERO_AVAILABLE = False


MIN_THROTTLE = 0.05
MAX_THROTTLE = 0.10


@dataclass
class MotorState:
    left_speed: float = 0.0
    right_speed: float = 0.0


class MotorController:
    def __init__(self, motor_configs: list[MotorConfig]):
        self.configs = motor_configs
        self.state = MotorState()
        self.factory = None
        self.esc_left = None
        self.esc_right = None
        self.is_available = False

        if not GPIOZERO_AVAILABLE:
            print("gpiozero not available, motor controller disabled")
            return

        try:
            self.factory = LGPIOFactory()

            left_pin = None
            right_pin = None

            for config in self.configs:
                if config.enabled:
                    if config.left:
                        left_pin = config.pin
                    else:
                        right_pin = config.pin

            if left_pin is not None and right_pin is not None:
                self.esc_left = PWMOutputDevice(
                    left_pin, pin_factory=self.factory, frequency=50
                )
                self.esc_right = PWMOutputDevice(
                    right_pin, pin_factory=self.factory, frequency=50
                )

                print("Arming ESCs... Turn on motors now!!!")
                self.esc_left.value = MAX_THROTTLE
                self.esc_right.value = MAX_THROTTLE

                input("Input anything once motors have been armed (the beeps change)")
                for i in reversed(range(5)):
                    print(f"{i}s")
                    time.sleep(1)

                self.esc_left.value = MIN_THROTTLE
                self.esc_right.value = MIN_THROTTLE
                print("ESCs armed")

                for i in reversed(range(5)):
                    print(f"{i}s")
                    time.sleep(1)

                self.is_available = True
        except Exception as e:
            print(f"Failed to initialize motor controller: {e}")
            self.cleanup()

    def percent_to_duty_cycle(self, percent: float) -> float:
        percent = max(0.0, min(100.0, float(percent)))

        if percent == 0.0:
            return MIN_THROTTLE

        base_duty = MIN_THROTTLE + (percent / 100.0) * (MAX_THROTTLE - MIN_THROTTLE)
        return min(MAX_THROTTLE, base_duty + 0.005)

    def set_speed(self, left_percent: float, right_percent: float):
        if not self.is_available:
            return

        self.state.left_speed = left_percent
        self.state.right_speed = right_percent

        left_duty = self.percent_to_duty_cycle(left_percent)
        right_duty = self.percent_to_duty_cycle(right_percent)

        self.esc_left.value = left_duty
        self.esc_right.value = right_duty

    def set_tank_steering(self, forward: float, turn: float):
        if not self.is_available:
            return

        left_config = next((c for c in self.configs if c.left), None)
        right_config = next((c for c in self.configs if not c.left), None)

        min_speed = left_config.min_speed if left_config else 0
        max_speed = left_config.max_speed if left_config else 1.0

        forward = max(-1.0, min(1.0, forward))
        turn = max(-1.0, min(1.0, turn))

        left = forward + turn
        right = forward - turn

        max_val = max(abs(left), abs(right), 1.0)
        left = left / max_val
        right = right / max_val

        if left_config and left_config.reversed:
            left = -left
        if right_config and right_config.reversed:
            right = -right

        left_percent = ((left + 1) / 2) * 100
        right_percent = ((right + 1) / 2) * 100

        left_percent = max(min_speed * 100, min(max_speed * 100, left_percent))
        right_percent = max(min_speed * 100, min(max_speed * 100, right_percent))

        self.set_speed(left_percent, right_percent)

    def stop(self):
        self.set_speed(0, 0)

    def cleanup(self):
        if self.esc_left:
            self.esc_left.value = 0
            self.esc_left.close()
        if self.esc_right:
            self.esc_right.value = 0
            self.esc_right.close()
        self.is_available = False
