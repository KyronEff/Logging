import traceback
import queue
import time
import atexit
import threading
from .batching_handler import HandleBatching

class HandleOutput:

    def __init__(self, output_config, batch_config, file):
        self.terminal_output = output_config["terminal"]
        self.file_output = output_config["file"]
        self.batch_config_toggle = batch_config["batch_logging"]

        self.file_path = file


        self.batcher = HandleBatching(file, batch_config)

        self._exit_flag = False

        self.log_buffer = []

        self.log_queue = queue.Queue()

        self.bg_task = threading.Thread(target=self._process_logs, daemon=True)
        self.bg_task.start()

        

        atexit.register(self._flush_on_exit)

    def _flush_on_exit(self):
        self.batcher.flush(self.log_buffer, override=True)
        self._exit_flag = True
        self.log_queue.put(None)

        self.bg_task.join()

    def _process_logs(self):
        
        while not self._exit_flag:
            message = self.log_queue.get(timeout=15)
            if message is None:
                break
            self.handle_log_output(message)

    def handle_log_output(self, message):

        if self.batch_config_toggle:

            if self.batcher.check_batching_condition(self.log_buffer):

                self.batcher.flush(self.log_buffer)

            else:

                    self.log_buffer.append(message)
        else:

            if self.terminal_output:

                print(message, flush=True)

            if self.file_output:

                    with open(self.file_path, 'a', encoding='utf-8') as log_file:
                        log_file.write(f"{message}\n")




    @staticmethod
    def log_internal_message(message, exception_traceback=None):

        print(f"\033[1;37m[INTERNAL] {message}")

        if exception_traceback:

            print(
                f"{traceback.format_exception(None, exception_traceback, exception_traceback.__traceback__)}")
