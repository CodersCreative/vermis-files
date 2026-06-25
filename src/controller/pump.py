from config import PumpConfig

try:
    from gpiozero import Motor

    GPIOZERO_AVAILABLE = True
except ImportError:
    GPIOZERO_AVAILABLE = False


class PumpController:
    def __init__(self, pump_configs: list[PumpConfig]):
        self.configs = pump_configs
        self.pumps = []
        self.is_available = False

        if not GPIOZERO_AVAILABLE:
            print("gpiozero not available, pump controller disabled")
            return

        for config in self.configs:
            if config.enabled:
                try:
                    self.pumps.append(
                        Motor(
                            forward=config.forward_pin,
                            backward=config.backward_pin,
                            enable=config.enable_pin,
                        )
                    )
                    self.is_available = True
                except Exception as e:
                    print(
                        f"Failed to initialize pump on pins {config.forward_pin}/{config.backward_pin}: {e}"
                    )

    def start(self):
        if not self.is_available:
            return
        for pump in self.pumps:
            pump.forward()

    def stop(self):
        if not self.is_available:
            return
        for pump in self.pumps:
            pump.stop()

    def cleanup(self):
        for pump in self.pumps:
            pump.stop()
            pump.close()
        self.pumps = []
        self.is_available = False
