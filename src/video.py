import cv2
import base64
import threading
import time
from fastapi import Response
from nicegui import app, ui

def get_placeholder() -> Response:
    black = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdjYGBg+A8AAQQBAHAgZQsAAAAASUVORK5CYII="
    return Response(
        content=base64.b64decode(black.encode("ascii")), media_type="image/png"
    )


class VideoManager:
    _instances = {}
    _registry_lock = threading.Lock()

    @classmethod
    def get_instance(cls, key : str, source):
        with cls._registry_lock:
            if key not in cls._instances:
                cls._instances[key] = cls(key, source)
            elif cls._instances[key].source != source:
                cls._instances[key].shutdown()
                cls._instances[key] = cls(key, source)
                
            return cls._instances[key]

    def __init__(self, key : str, source):
        self.source = source
        self.key = key
        self.cap = cv2.VideoCapture(source)
        self.last_frame = None
        self.frame_lock = threading.Lock()

        self.thread_running = True
        self.worker = threading.Thread(target=self.video_worker, daemon=True)
        self.worker.start()
        self.route_path = f"/video/stream/{key}"        

        self.register_route()

    def video_worker(self):
        while self.thread_running:
            if self.cap is not None and self.cap.isOpened():
                success, frame = self.cap.read()
                if success and frame is not None:
                    try:
                        _, imencode_image = cv2.imencode(".jpg", frame)
                        data = imencode_image.tobytes()

                        with self.frame_lock:
                            self.last_frame = data
                    except Exception as e:
                        print(f"Error on {self.key} : {self.source}: {e}")
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.1)

    def register_route(self):
        @app.get(self.route_path)
        def grab_video_frame() -> Response:
            with self.frame_lock:
                frame_bytes = self.last_frame

            if frame_bytes is None:
                return get_placeholder()

            return Response(content=frame_bytes, media_type="image/jpeg")

    def shutdown(self):
        self.thread_running = False
        with self.frame_lock:
            if self.cap is not None:
                try:
                    self.cap.release()
                except:
                    pass
                self.cap = None
            self.last_frame = None


class CV2Video:
    def __init__(self, key : str, source=0):
        self.manager = VideoManager.get_instance(key, source)
        self.video = None
        self.key = key

    def change_source(self, source=0):
        self.manager = VideoManager.get_instance(self.key, source)        

    def render(self):
        self.video = ui.interactive_image(self.manager.route_path).classes(
            "w-full h-full"
        )
        ui.timer(interval=0.03, callback=self.video.force_reload)
        return self.video
