from .output_handler import HandleOutput
import time
import threading

class HandleBatching:

    def __init__(self, file, batch_config):

        self.file_path = file

        self.log_buffer_max_size = batch_config["batch_size"]
        self.flush_interval = batch_config["flush_interval"]

        self._lock = threading.Lock()

        self.last_flush_time = time.time()

    def flush(self, buffer, override= False):

        with self._lock:

            if buffer or override:

                with open(self.file_path, 'a', encoding='utf-8') as log_file:
                    log_file.write('\n'.join(buffer) + '\n')

                buffer.clear()
                self.last_flush_time = time.time()
                HandleOutput.log_internal_message(f"Flushed {self.log_buffer_max_size} logs")

    def check_batching_condition(self, buffer):

            if len(buffer) >= self.log_buffer_max_size \
                or time.time() - self.last_flush_time >= self.flush_interval:

                return True
            
            return False

