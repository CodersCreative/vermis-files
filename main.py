import json;
import cv2;
import numpy as np
from ultralytics import YOLO
from gpiozero import AngularServo;
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
        servos : dict(str, list(int)) = config["servo_pins"];

        def create_servo(pin : int) -> AngularServo:
            return AngularServo(pin, min_angle=0, max_angle=180, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000); 

        self.linkages = [create_servo(pin) for pin in servos["linkages"]];
        self.arms = [create_servo(pin) for pin in servos["arms"]];
        self.pumps = [create_servo(pin) for pin in servos["pumps"]];
        
        self.pumps_activated = False;        

    def set_linkage_height(self, percent : float):
        for servo in self.linkages:
            servo.angle = clamp(percent, 0, 1) * 90;

    def set_arm_height(self, percent : float):
            for servo in self.arms:
                servo.angle = clamp(percent, 0, 1) * 60;
                
    def activate_pump(self):
        for servo in self.pumps:
            if not self.pumps_activated:
                servo.angle = 90;
            else:
                servo.angle = 0;

class PestDetection:
    def __init__(self, config : dict):
        self.model = YOLO(config["yolo"]["path"]);
        self.cap = cv2.VideoCapture(config["capture"]["ip_address"]);
        self.resolution = {"x" : config["capture"]["resolution"]["x"], "y" : config["capture"]["resolution"]["y"]};
        self.min_confidence = config["yolo"]["min_confidence"];

    def capture(self) -> np.ndarray:
        ret, frame = self.cap.read();
        frame : np.ndarray = cv2.resize(frame, (self.resolution["x"], self.resolution["y"]));
        return frame;

    def severity(self, capture : np.ndarray) -> float:
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
    for interval in range(LINKAGE_HEIGHT_INTERVALS):
        servos.set_linkage_height(interval / LINKAGE_HEIGHT_INTERVALS);
    
        if timeout > 0:
            timeout -= 1;
            continue;

        severity : float = detection.severity(detection.capture());
        if severity > 0:
            servos.activate_pump();
            sleep(severity * MAX_SPRAY_TIME);
            servos.activate_pump();
            timeout = 2;
            
        
    for interval in range(ARM_HEIGHT_INTERVALS):
        servos.set_arm_height(interval / ARM_HEIGHT_INTERVALS);
          
        if timeout > 0:
            timeout -= 1;
            continue;

        severity : float = detection.severity(detection.capture());
        if severity > 0:
            servos.activate_pump();
            sleep(severity * MAX_SPRAY_TIME);
            servos.activate_pump();
            timeout = 2; 

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
