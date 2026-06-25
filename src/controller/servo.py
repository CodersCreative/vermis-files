import time
from dataclasses import dataclass
from config import ServoConfig, ServoType

try:
    from gpiozero import AngularServo, Servo
    from gpiozero.pins.lgpio import LGPIOFactory

    GPIOZERO_AVAILABLE = True
except ImportError:
    GPIOZERO_AVAILABLE = False


@dataclass
class ArmState:
    base: float = 0.0
    mid: float = 0.0
    top: float = 0.0


class ServoController:
    def __init__(self, servo_configs: list[ServoConfig]):
        self.configs = servo_configs
        self.state = ArmState()
        self.factory = None
        self.servos = []
        self.is_available = False

        if not GPIOZERO_AVAILABLE:
            print("gpiozero not available, servo controller disabled")
            return

        try:
            self.factory = LGPIOFactory()

            for config in self.configs:
                if config.enabled:
                    if config.continuous:
                        servo = Servo(
                            config.pin,
                            pin_factory=self.factory,
                            min_pulse_width=0.5 / 1000,
                            max_pulse_width=2.5 / 1000,
                        )
                        self.servos.append(
                            {
                                "servo": servo,
                                "config": config,
                                "last": 0.0,
                                "continuous": True,
                            }
                        )
                        servo.value = 0
                    else:
                        servo = AngularServo(
                            config.pin,
                            pin_factory=self.factory,
                            min_angle=config.min_angle,
                            max_angle=config.max_angle,
                            min_pulse_width=0.5 / 1000,
                            max_pulse_width=2.5 / 1000,
                        )
                        self.servos.append(
                            {
                                "servo": servo,
                                "config": config,
                                "last": config.offset,
                                "continuous": False,
                            }
                        )
                        servo.angle = config.offset

            self.is_available = len(self.servos) > 0
        except Exception as e:
            print(f"Failed to initialize servo controller: {e}")
            self.cleanup()

    def set_servo_angle(self, index: int, angle: float):
        if not self.is_available or index >= len(self.servos):
            return

        servo_data = self.servos[index]
        config = servo_data["config"]

        if servo_data["continuous"]:
            speed = max(-1.0, min(1.0, angle))
            if abs(speed - servo_data["last"]) < config.deadband:
                return
            servo_data["servo"].value = speed
            servo_data["last"] = speed
        else:
            angle = max(config.min_angle, min(config.max_angle, angle + config.offset))
            if abs(angle - servo_data["last"]) < config.deadband:
                return
            servo_data["servo"].angle = angle
            servo_data["last"] = angle

        time.sleep(config.interval)

    def set_arm_angles(self, base: float, mid: float, top: float):
        self.state.base = base
        self.state.mid = mid
        self.state.top = top

        for i, servo_data in enumerate(self.servos):
            config = servo_data["config"]

            if config.type == ServoType.BASE_ARM.value:
                self.set_servo_angle(i, base)
            elif config.type == ServoType.MID_ARM.value:
                self.set_servo_angle(i, mid)
            elif config.type == ServoType.TOP_ARM.value:
                self.set_servo_angle(i, top)

    def get_servo_by_type(self, servo_type: int) -> int:
        for i, servo_data in enumerate(self.servos):
            if servo_data["config"].type == servo_type:
                return i
        return -1

    def stop(self):
        if not self.is_available:
            return
        for servo_data in self.servos:
            servo_data["servo"].detach()

    def cleanup(self):
        for servo_data in self.servos:
            servo_data["servo"].close()
        self.servos = []
        self.is_available = False
