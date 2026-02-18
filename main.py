import json;
import cv2;
import numpy as np
from gpiozero import AngularServo;
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep;

CONFIG_PATH : str = "config.json";
LINKAGE_HEIGHT_INTERVALS : int = 5;
ARM_HEIGHT_INTERVALS : int = 3;
MAX_SPRAY_TIME : float = 5;

def get_config_data(path : str) -> dict:
    with open(path, "r") as file:
        return json.load(file);

def clamp(num, min_num, max_num):
    return max(min_num, min(num, max_num));

class Servos:
    def __init__(self, config : dict):
        servos : dict = config["servo_pins"];

        def create_servo(pin : int) -> AngularServo:
            factory = PiGPIOFactory();
            return AngularServo(pin, min_angle=0, max_angle=360, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory); 

        self.linkages = [create_servo(pin) for pin in servos["linkages"]];
        self.linkage_hold_time = servos["linkage_hold_time"];
        self.arms = [create_servo(pin) for pin in servos["arms"]];
        self.pumps = [create_servo(pin) for pin in servos["pumps"]];
        self.linkages_activated = False;
        self.pumps_activated = False;        

    def activate_linkags(self):
        for servo in self.linkages:
            if self.linkages_activated:
                servo.angle = 30;
            else :
                servo.angle = 0;

    def set_arm_height(self, percent : float):
            for servo in self.arms:
                servo.angle = clamp(percent, 0, 1) * 70;
                
    def activate_pump(self):
        for servo in self.pumps:
            if self.pumps_activated:
                servo.angle = 50;
            else:
                servo.angle = 0;

class PestDetection:
    def __init__(self, config : dict):
        if not config["capture"]["enabled"]:
            self.enabled = False;
            return;
        self.enabled = True;

        if config["yolo"]["enabled"]:
            self.yolo_enabled = True;
            from ultralytics import YOLO            
            self.model = YOLO(config["yolo"]["path"]);
        self.yolo_enabled = False;
        self.cap = cv2.VideoCapture(config["capture"]["ip_address"]);
        self.resolution = {"x" : config["capture"]["resolution"]["x"], "y" : config["capture"]["resolution"]["y"]};
        self.min_confidence = config["yolo"]["min_confidence"];

    def capture(self) -> np.ndarray:
        ret, frame = self.cap.read();
        frame : np.ndarray = cv2.resize(frame, (self.resolution["x"], self.resolution["y"]));
        return frame;

    def severity(self, capture : np.ndarray) -> float:
        if not self.yolo_enabled: 0.0;
        results = self.model(capture, verbose=False);
        detections = results[0].boxes;
        detection_amt : int = len(detections);

        severity = 0.0;

        for detection in detections:
            conf = detection.cong.item();
            if conf < self.min_confidence:
                continue;

            severity += conf / detection_amt;
        
        return severity;
       
        
def spray_pests(servos : Servos, detection : PestDetection):
    timeout : int = 0;
            
    def handle_severity() -> bool:
        severity : float = detection.severity(detection.capture());
        if severity > 0:
            servos.activate_pump();
            sleep(severity * MAX_SPRAY_TIME);
            servos.activate_pump();
            timeout = 2;
            return true;
        return false;

    if handle_severity(): return;    
    self.activate_linages();    
    if handle_severity(): return;

    for interval in range(ARM_HEIGHT_INTERVALS):
        servos.set_arm_height(interval / ARM_HEIGHT_INTERVALS);
          
        if timeout > 0:
            timeout -= 1;
            continue;

        if handle_severity(): return;

    self.activate_linages();

class Movement:
    def __init__(self, config : dict):
        pass

    def next_plant(self):
        pass

    def have_break(self):
        pass
        
def main():
    config : dict = get_config_data(CONFIG_PATH);
    servos : Servos = Servos(config);
    detection : PestDetection = PestDetection(config);
    movement : Movement = Movement(config);

    while True:
        spray_pests(servos, detection);
        movement.next_plant();

if __name__ == "__main__":
    main();
