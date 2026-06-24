from nicegui import app, ui
from video import CV2Video

SOURCES = {
    "forward" : 0,
    "backward" : 0,
    "arm" : 0,
}

class VermisApp:
    def __init__(self):
        self.video = None

    def setup(self):
        self.video = CV2Video("main", SOURCES["forward"])

    def home(self):
        with ui.tabs().classes("w-full h-full object-cover") as tabs:
            ui.tab("forward")
            ui.tab("backward")
            ui.tab("arm")
        with ui.tab_panels(tabs, value="forward").classes("w-full object-cover "):
            with ui.tab_panel("forward"):
                if self.video:
                    self.video.change_source(SOURCES["forward"])
                    self.video.render()
            with ui.tab_panel("backward"):
                if self.video:
                    self.video.change_source(SOURCES["backward"])
                    self.video.render()
            with ui.tab_panel("arm"):
                if self.video:
                    self.video.change_source(SOURCES["arm"])                
                    self.video.render()

        with ui.card().classes("absolute-center z-10 shadow-lg"):
            ui.label("Hello")

instance = VermisApp()  # ("http://192.168.0.104:8080/video")
instance.setup()


@ui.page("/")
def index():
    instance.home()


if __name__ == "__main__":
    ui.run(title="VERMIS", reload=False)
