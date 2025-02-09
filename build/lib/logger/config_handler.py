from .output_handler import HandleOutput
import os
import json
import sys


class HandleConfigs:

    FALLBACK_CONFIGURATION = {
    "log_components": {
        "color": True,
        "timestamp": True,
        "timestamp_format": "%Y-%m-%d / %Hh-%Mm-%Ss",
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
        },
        "DEFAULT" : {
            "color": "\033[1;33m",
            "level": "DEFAULT",
            "traceback": True
        }
    },
    "file_locations": {
        "log_file_path": "{CURRENT_PATH}"
    },
    "log_rotation_configs": {
        "log_rotation": False,
        "size_rotation": True,
        "max_file_size": 10,
        "time_rotation": False,
        "max_file_age": 1,
        "check_interval": 30
    },

    "batch_logging_configs" : {
        "batch_logging": True,
        "batch_size": 10,
        "flush_interval": 45,
        "check_interval": 10
    },

    "output_configs": {
        "terminal": True,
        "file": True
    }
}

    def __init__(self, config_path):

        if config_path is None:
            config_path = os.path.join(os.path.dirname(
                __file__), 'Logger_primary_config.JSON')

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
            path = os.path.join(os.path.dirname(sys.argv[0]), 'log.txt')

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
