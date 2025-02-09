from .config_handler import HandleConfigs
from .log_compiler import CompileLog
from .output_handler import HandleOutput
from .bg_rotation import BgRotation

class Logger:

 # initialization function
    _compiler = None
    _output = None

    def __init__(self, config_path=None):

        self.configs = HandleConfigs(config_path).get_valid_config()

        if not Logger._compiler:
            Logger._compiler = CompileLog(
                self.configs["error_map"], self.configs["log_components"])
        if not Logger._output:
            Logger._output = HandleOutput(self.configs["output_configs"], self.configs["batch_logging_configs"], self.configs["file_locations"]["log_file_path"])

        self._compiler = Logger._compiler
        self._output = Logger._output

        if self.configs["log_rotation_configs"]["log_rotation"]:
            rotation_task = BgRotation(self.configs)


    def log(self, message, level, exception_traceback=None):

        message = self._compiler.build_log(message, level, exception_traceback)
        self._output.log_queue.put(message)

logx = Logger()

