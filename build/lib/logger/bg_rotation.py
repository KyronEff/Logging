import threading
import signal
import time
from rotation_handler import HandleRotation


class BgRotation:

    def __init__(self, configs):

        self.load_configs(configs)
        self._rotation_handler = HandleRotation(self.full_configs)

        self.signals = [signal.SIGINT, signal.SIGTERM]
        self.create_signal()

        self.loop_break_key = threading.Event()

        self.task = threading.Thread(target=self.bg_rotation_check, daemon=True)
        self.task.start()

    def load_configs(self, configs):

        try:

            self.full_configs = configs
            self.interval = configs["log_rotation_configs"]["check_interval"]

        except KeyError as key_error:
            raise KeyError("Could not find log rotation configs. Log rotation is disabled.") from key_error

    def bg_rotation_check(self):

        while not self.loop_break_key.is_set():
            self._rotation_handler.rotate_log_path()

            time.sleep(self.interval)

    def break_task(self, signum, frame):
        self.loop_break_key.set()

    def create_signal(self):

        for signal_type in self.signals:
            signal.signal(signal_type, self.break_task)
