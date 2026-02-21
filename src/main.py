from settings import SettingsPopUp;
from settings import *;
from config import Config;
from constants import *;
import customtkinter as ctk;
import cv2;
from PIL import Image;

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=ALTERNATE_DARK_COLOUR);
        self.title("The Vermis App");
        self.geometry(f"{WINDOW_SIZE['x']}x{WINDOW_SIZE['y']}");
        ctk.DrawEngine.preferred_drawing_method = "circle_shapes";
        ctk.set_widget_scaling(2);
        ctk.set_appearance_mode("dark");

        self.video_widget = ctk.CTkLabel(self, text="");
        self.video_widget.pack(pady=20);

        self.config = Config.load_from_file(CONFIG_PATH);
        
        self.settings = None;
        self.width, self.height = self.config.capture.resolution["x"], self.config.capture.resolution["y"];

        self.handle_vid_feed();
        self.start_camera();

        self.bind('<Escape>', lambda e: self.quit_app());
        self.protocol("WM_DELETE_WINDOW", self.quit_app);
        self.open_settings();

    def handle_vid_feed(self):
        if self.config.capture.use_webcam:
            self.vid = cv2.VideoCapture(0);
        else:
            # TODO Other feeds
            self.vid = cv2.VideoCapture(0);  

    def start_camera(self):
        success, frame = self.vid.read()
        
        if success:
            opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB);
            captured_image = Image.fromarray(opencv_image);
            photo_image = ctk.CTkImage(light_image=captured_image, dark_image=captured_image, size=(self.width, self.height));
            self.video_widget.configure(image=photo_image);
            self.video_widget.after(10, self.start_camera);

    def open_settings(self):
        if self.settings is None:
            self.settings = SettingsPopUp(self);
        
    def quit_app(self):
        self.vid.release();
        self.destroy();

if __name__ == "__main__":
    app = App()
    app.mainloop()
