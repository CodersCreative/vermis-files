from time import sleep
from collections.abc import Iterator
from dataclasses import dataclass
from inputs import get_gamepad

@dataclass
class Vector2:
    x : float = 0;
    y : float = 0;

class MovementESCs:
    def __init__(self, left : list[int], right : list[int], max : float):
        self.left_pins = left;
        self.right_pins = right;
        self.max = max;

        if len(self.left_pins) <= 0 and len(self.right_pins) <= 0:
            self.is_available = False;
            return

        try:
            from gpiozero import AngularServo
            from gpiozero.pins.pigpio import PiGPIOFactory
            
            self.left = [AngularServo(
                pin,
                min_pulse_width=1 / 1000,
                max_pulse_width=2 / 1000,
                pin_factory=PiGPIOFactory(),
            ) for pin in self.left_pins];

            self.right = [AngularServo(
                pin,
                min_pulse_width=1 / 1000,
                max_pulse_width=2 / 1000,
                pin_factory=PiGPIOFactory(),
            ) for pin in self.right_pins]            

            self.is_available = True;
        except Exception as exc:
            try:
                from gpiozero import AngularServo
            
                self.left = [AngularServo(
                    pin,
                    min_pulse_width=1 / 1000,
                    max_pulse_width=2 / 1000,
                ) for pin in self.left_pins];

                self.right = [AngularServo(
                    pin,
                    min_pulse_width=1 / 1000,
                    max_pulse_width=2 / 1000,
                ) for pin in self.right_pins]            

                self.is_available = True;
            except Exception as fallback_exc:
                self.is_available = False;
                print("1st error : {}\n2nd error : {}".format(exc, fallback_exc));

        if self.is_available:
            for esc in self.left:
                esc.min()

            for esc in self.right:
                esc.min()
                
            sleep(5);

            print("ESCs initialized")
           
    def set_speed(self, value : float, is_left : bool):
        if not self.is_available:
            return

        value = max(-1.0, min(1.0, value)) * self.max
        target_escs = self.left if is_left else self.right
        
        for esc in target_escs:
            esc.value = value        
    
    def set_move_vector(self, vector : Vector2):
        if not self.is_available:
            return        

        right_speed = vector.y + vector.x
        right_speed = vector.y - vector.x
        
        max_input = max(abs(right_speed), abs(right_speed), 1.0)
        
        left_speed = right_speed / max_input
        right_speed = right_speed / max_input

        self.set_speed(left_speed, is_left=True)
        self.set_speed(right_speed, is_left=False)
  

def get_move_thumbstick_vector() -> Iterator[Vector2]:
    MAX_VAL = 32767
    x = 0;
    y = 0;
    
    while True:
        events = get_gamepad()
        for event in events:
            changed = False;
            if event.code == 'ABS_X':
                new_x = event.state / MAX_VAL
                if new_x != x:
                    changed = True;
                    x = new_x
            
            elif event.code == 'ABS_Y':
                new_y = event.state / MAX_VAL
                if new_y != y:
                    changed = True;
                    y = new_y                

            if changed:
                yield Vector2(round(x, 2), round(y, 2))


def main():
    movement = MovementESCs([], [], 0.2);
    for vector in get_move_thumbstick_vector():
        print("Left Thumbstick Input : {}".format(vector));
        movement.set_move_vector(vector);

if __name__ == "__main__":
    main()
