import traceback
import os
import json
import random
import asyncio
from datetime import datetime, timedelta

class Logger:

 # initialization function
    _compiler = None
    _output = None
    stop_rotation = False

    def __init__(self, config_path=None):

        self.configs = HandleConfigs(config_path).get_valid_config()

        if not Logger._compiler:
            Logger._compiler = CompileLog(
                self.configs["error_map"], self.configs["log_components"])
        if not Logger._output:
            Logger._output = HandleOutput(self.configs["output_configs"])

        self._compiler = Logger._compiler
        self._output = Logger._output

    def log(self, message, level, exception_traceback=None):

        message = self._compiler.build_log(message, level, exception_traceback)
        self._output.handle_log_output(message, self.configs["file_locations"]["log_file_path"])


class CompileLog:

    def __init__(self, error_map, log_components):

        self.error_map = error_map
        self.log_components = log_components

    def build_log(self, message, error_level, exception_traceback=None):

        error_level = error_level or "UNKNOWN"

        if error_level in self.error_map:

            return ''.join([
                FormatComponents.get_color(
                    self.error_map, error_level) if self.log_components["color"] else "",
                FormatComponents.get_timestamp(
                    self.log_components) if self.log_components["timestamp"] else "",
                f"[{error_level}] " if self.log_components["level"] else "",
                f"{message}" if self.log_components["message"] else "",
                FormatComponents.get_traceback(
                    exception_traceback) if self.error_map[error_level]["traceback"] and exception_traceback else ""
            ])

        return f"[{error_level}] {message}" + (f"\n{FormatComponents.get_traceback(exception_traceback)}" if exception_traceback else "")


class FormatComponents:

    @staticmethod
    def get_color(error_map, error_level):

        return error_map[error_level]["color"].encode().decode("unicode_escape")

    @staticmethod
    def get_timestamp(log_components):

        return f"[{datetime.now().strftime(log_components['timestamp_format'])}]\n"

    @staticmethod
    def get_traceback(error):

        if error is None:

            HandleOutput.log_internal_message("No error was provided")
            return ""

        if not isinstance(error, Exception):
            if callable(error):

                error = error("Error passed with no message")
            else:
                HandleOutput.log_internal_message("Invalid error type or message")
                return ""

        if not hasattr(error, '__traceback__'):

            return "\nNo traceback provided"

        return "\n\033[0m" + ''.join(traceback.format_exception(None, error, error.__traceback__))


class HandleOutput:

    def __init__(self, output_config):
        self.terminal_output = output_config["terminal"]
        self.file_output = output_config["file"]

    def handle_log_output(self, message, file):

        if self.terminal_output:

            print(message)

        if self.file_output:

            with open(file, 'a', encoding='utf-8') as log_file:
                log_file.write(f"{message}\n")

    @staticmethod
    def log_internal_message(message, exception_traceback=None):

        print(f"\033[1;37m[INTERNAL] {message}")

        if exception_traceback:

            print(f"{traceback.format_exception(None, exception_traceback, exception_traceback.__traceback__)}")


class HandleConfigs:

    FALLBACK_CONFIGURATION = {

        "log_components": {
            "color": True,
            "timestamp": True,
            "timestamp_format": r"%Y-%m-%d / %Hh-%Mm-%Ss",
            "message": True,
            "level": True
        },

        "error_map": {
            "INFO": {
                "color": "\\033[0;34m",
                "level": "INFO",
                "traceback": False
            },

            "DEBUG": {
                "color": "\\033[0;35m",
                "level": "DEBUG",
                "traceback": True
            },

            "ERROR": {
                "color": "\\033[0;31m",
                "level": "ERROR",
                "traceback": False
            },

            "WARNING": {
                "color": "\\033[1;33m",
                "level": "WARNING",
                "traceback": True
            },

            "CRITICAL": {
                "color": "\\033[1;35m",
                "level": "CRITICAL",
                "traceback": True
            }

        },

        "file_locations": {

            "log_file_path": "{CURRENT_PATH}"

        },

        "log_rotation_configs": {

            "log_rotation": False,
            "size_rotation": True,
            "max_file_size": 5242880,
            "time_rotation": False,
            "max_file_age": 1

        },

        "output_configs": {

            "terminal": True,
            "file": True

        }
    }

    def __init__(self, config_path):

        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'Logger_primary_config.JSON')

        HandleOutput.log_internal_message(
            f"Attempting to load configs from {config_path}")
        self.configs = self.get_config_map(config_path)
        HandleOutput.log_internal_message("Initialising configuration file")

    def get_valid_config(self):

        self.validate_config_types(self.configs)
        self.validate_log_path()
        return self.configs

    def get_config_map(self, config_path):

        try:

            with open(config_path, 'r') as config:

                HandleOutput.log_internal_message(
                    "Custom config file successfully loaded")
                return json.load(config)

        except (FileNotFoundError, PermissionError, json.JSONDecodeError):

            with open(config_path, 'w') as config_file:

                HandleOutput.log_internal_message(
                    f"Specified config file could not be found or accessed.\nAttempting to create a file with default configurations as 'Logger_primary_config.JSON' at {config_path}.")
                json.dump(HandleConfigs.FALLBACK_CONFIGURATION,
                          config_file, indent=4)

            return HandleConfigs.FALLBACK_CONFIGURATION

    def validate_config_types(self, configs=None):

        if configs is None:
            configs = self.configs

        FALLBACK = HandleConfigs.FALLBACK_CONFIGURATION

        for key, value in configs.items():

            if key not in FALLBACK:
                HandleOutput.log_internal_message(
                    "Specified config uses malformed or corrupted data. Using Fallback")
                self.configs = FALLBACK
                return

            fallback = FALLBACK[key]

            if isinstance(value, dict) and isinstance(fallback, dict):

                for subkey, subvalue in value.items():

                    if subkey not in fallback:
                        HandleOutput.log_internal_message(
                            "Specified config uses malformed or corrupted data. Using Fallback")
                        self.configs = FALLBACK
                        return

                    subfallback = FALLBACK[key][subkey]

                    if isinstance(fallback[subkey], dict):

                        if not isinstance(subvalue, type(subfallback)):
                            HandleOutput.log_internal_message(
                                f"Encountered TypeError. Expected {type(subfallback)} but found {type(subvalue)}")
                            configs[key][subkey] = subfallback
                            continue

                continue

            if not isinstance(value, type(fallback)):
                HandleOutput.log_internal_message(
                    f"Encountered TypeError. Expected {type(fallback)} but found {type(value)}")
                configs[key] = fallback
                continue

    def validate_log_path(self):

        path = self.configs["file_locations"]["log_file_path"]

        if path == "{CURRENT_PATH}":
            path = os.path.join(os.path.dirname(__file__), "log.txt")

        try:

            with open(path, 'a', encoding='utf-8'):

                self.configs["file_locations"]["log_file_path"] = path
                HandleOutput.log_internal_message(
                    f"Log file found or created. Using {path}.")

        except (FileNotFoundError, PermissionError) as error:

            self.configs["output_configs"]["file"] = False
            self.configs["log_rotation_configs"]["log_rotation"] = False
            HandleOutput.log_internal_message(
                f"Path [{path}] to the log file couldn't be found, or can't be accessed. Disabled file rotation and logging", exception_traceback=error)


class HandleRotation:

    def __init__(self, configs):
        self.file_path = configs["file_locations"]["log_file_path"]
        self.log_rotation = configs["log_rotation_configs"]

    async def bg_rotation_check(self, interval=120):

        while not Logger.stop_rotation:
            self.rotate_log_path()

            await asyncio.sleep(interval)

    def begin_bg_rotation(self):

        if not Logger.stop_rotation:
            task = asyncio.get_event_loop().create_task(self.bg_rotation_check())

    def break_bg_rotation(self, task):

        if task:
            asyncio.Event.clear(task)

    def check_rotation_condition(self, full_path, max_size, max_time):

        if os.path.getsize(full_path) >= max_size or datetime.now() - datetime.fromtimestamp(os.path.getctime(full_path)) >= timedelta(days=max_time):
            return True
        return False

    def rotate_log_path(self):

        HandleOutput.log_internal_message("Running rotation check")

        if self.check_rotation_condition(self.file_path,
                                         self.log_rotation["max_file_size"],
                                         self.log_rotation["max_file_age"]
                                         ):

            try:

                self.full_rotation()

            except (FileNotFoundError, PermissionError) as error:

                HandleOutput.log_internal_message(
                    "An error occured whilst attempting log rotation.", exception_traceback=error)

    def rename_rotating_log(self, log_file_path):
        archive_name = f"log_archive {datetime.now().strftime('%d_%m_%y %H_%M_%S')}_{random.randint(1000, 9999)}.txt"

        os.rename(log_file_path, archive_name)
        HandleOutput.log_internal_message(
            f"Log file Archived as {archive_name}.\nArchived file size: {os.path.getsize(archive_name)}\nArchived file age: {os.path.getmtime(archive_name)}.")

    def create_fresh_log(self, log_file_path):

        with open(log_file_path, 'a') as new_log_file:
            HandleOutput.log_internal_message(
                f"Created new file as {new_log_file.name}")

    def full_rotation(self):

        self.rename_rotating_log(self.file_path)
        self.create_fresh_log(self.file_path)


logger = Logger()
try:

    raise TypeError

except TypeError as error:

    logger.log("Test", "DEBUG", exception_traceback=error)
