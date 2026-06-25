from nicegui import app, ui
from screens.control import ControlScreen
from screens.settings import SettingsScreen
from config import Config


class VermisApp:
    def __init__(self):
        self.config = Config.load_from_file()
        self.control = ControlScreen(self.config)
        self.settings = SettingsScreen()

    def cleanup(self):
        self.control.cleanup()


vermis = VermisApp()


@ui.page("/")
def settings():
    vermis.settings.render()


@ui.page("/control/")
def control():
    vermis.control.render()


@app.on_shutdown
def shutdown():
    vermis.cleanup()


if __name__ == "__main__":
    ui.run(title="VERMIS", reload=False)
