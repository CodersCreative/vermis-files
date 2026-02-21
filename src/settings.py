from constants import *;
from widgets import *;
import customtkinter as ctk;

class SettingsPopUp(ctk.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=ALTERNATE_DARK_COLOUR, **kwargs);
        self.title("Vermis Settings");
        self.geometry("1280x720");
        self.transient(master);
        self.grab_set();

        self.linkage_hold_time = ctk.DoubleVar(value=master.config.servo_pins.linkage_hold_time);        

        self.resolution_x = ctk.IntVar(value=master.config.capture.resolution["x"]);
        self.resolution_y = ctk.IntVar(value=master.config.capture.resolution["y"]);
        self.ip_address = ctk.StringVar(value=master.config.capture.ip_address);
        self.use_webcam = ctk.BooleanVar(value=master.config.capture.use_webcam);
        self.capture_enabled = ctk.BooleanVar(value=master.config.capture.enabled);

        self.min_confidence = ctk.DoubleVar(value=master.config.yolo.min_confidence);
        self.yolo_path = ctk.StringVar(value=master.config.yolo.path);        
        self.yolo_enabled = ctk.BooleanVar(value=master.config.yolo.enabled);

        self.master = master;  
                
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(anchor="center")

        # Servo Settings

        servo_label = ctk.CTkLabel(container, text="Servo Settings", font=SMALL_FONT);
        servo_label.pack(pady=PADDING_SMALL);

        seperate_linkage = Line(container);
        seperate_linkage.pack(pady=PADDING_SMALL, fill="x");

        linkage_hold_time = NamedSlider(container, label="Hold Time", input_var=self.linkage_hold_time,from_=0, to=5);
        linkage_hold_time.pack(pady=PADDING_SMALL, fill="x");

        # Captrue Settings

        capture_label = ctk.CTkLabel(container, text="Capture Settings", font=SMALL_FONT);
        capture_label.pack(pady=PADDING_SMALL, fill="x");

        seperate_capture = Line(container);
        seperate_capture.pack(pady=PADDING_SMALL, fill="x");

        row_frame = ctk.CTkFrame(container, fg_color="transparent")
        row_frame.pack(fill="x")

        capture_enabled = NamedCheckbox(row_frame, input_var=self.capture_enabled, label="Enabled");
        capture_enabled.pack(side="left", pady=PADDING_SMALL, fill="x", expand=True, padx=(0,PADDING_SMALL));           

        use_webcam = NamedCheckbox(row_frame, input_var=self.use_webcam, label="Use Webcam");
        use_webcam.pack(side="left", pady=PADDING_SMALL,  padx=(PADDING_SMALL, 0));        

        row_frame = ctk.CTkFrame(container, fg_color="transparent")
        row_frame.pack(fill="x")

        resolution_x = NamedEntry(row_frame, input_var=self.resolution_x, label="X Resolution");
        resolution_x.pack(side="left", pady=PADDING_SMALL, fill="x", padx=(0, PADDING_SMALL));

        resolution_y = NamedEntry(row_frame, input_var=self.resolution_y, label="Y Resolution");
        resolution_y.pack(side="left", pady=PADDING_SMALL, fill="x", padx=(PADDING_SMALL, 0));            

        ip_address = NamedEntry(container, input_var=self.ip_address, label="IP Address");
        ip_address.pack(pady=PADDING_SMALL, fill="x");        

        # Yolo Settings
                
        capture_label = ctk.CTkLabel(container, text="YOLO Settings", font=SMALL_FONT);
        capture_label.pack(pady=PADDING_SMALL, fill="x");

        seperate_capture = Line(container);
        seperate_capture.pack(pady=PADDING_SMALL, fill="x");

        capture_enabled = NamedCheckbox(container, input_var=self.yolo_enabled, label="Enabled");
        capture_enabled.pack(pady=PADDING_SMALL, fill="x");

        min_confidence = NamedSlider(container, label="Min Confidence", input_var=self.min_confidence,);
        min_confidence.pack(pady=PADDING_SMALL, fill="x");
        
        yolo_path = NamedEntry(container, input_var=self.yolo_path, label="Model Path");
        yolo_path.pack(pady=PADDING_SMALL, fill="x");
                    
        save = ctk.CTkButton(container, text="Save", command=self.save_settings, text_color=DEFAULT_COLOUR, fg_color=ACCENT_COLOUR)
        save.pack(pady=PADDING_SMALL, padx=PADDING_SMALL, fill="x")

        self.wait_window(self);
        
    def save_settings(self):
        self.master.config.servo_pins.linkage_hold_time = self.linkage_hold_time.get();
        
        self.master.config.capture.enabled = self.capture_enabled.get();
        self.master.config.capture.ip_address = self.ip_address.get();
        self.master.config.capture.resolution["x"] = self.resolution_x.get();
        self.master.config.capture.resolution["y"] = self.resolution_y.get();
        self.master.config.capture.use_webcam = self.use_webcam.get();
        
        self.master.config.yolo.enabled = self.yolo_enabled.get();
        self.master.config.yolo.min_confidence = self.min_confidence.get();
        self.master.config.yolo.path = self.yolo_path.get();

        self.master.config.save_to_file(CONFIG_PATH);
