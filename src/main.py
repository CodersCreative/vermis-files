from nicegui import app, ui
from screens.control import ControlScreen
from screens.settings import SettingsScreen
from video import CV2Video
from config import Config


class VermisApp:
    def __init__(self):
        self.config = Config.load_from_file()
        self.control = ControlScreen()
        self.settings = SettingsScreen()


vermis = VermisApp()  # ("http://192.168.0.104:8080/video")


@ui.page("/")
def settings():
    vermis.settings.render()


@ui.page("/control/")
def control():
    vermis.control.render()


if __name__ == "__main__":
    ui.run(title="VERMIS", reload=False)
