import traceback
import os
import json
import random
from datetime import datetime, timedelta
import asyncio
import signal
import sys

class Logger:

 # initialization function
    
    def __init__(self, 
                 config_path=None, 
                 ):
         
        self.configs = ConfigHandler(config_path).get_valid_config()

        self.LOG_COMPONENTS = self.configs.get("log_components")
        self.ERROR_MAP = self.configs.get("error_map")
        self.FILE_LOCATIONS = self.configs.get("file_locations")
        self.LOG_ROTATION = self.configs.get("log_rotation")
        self.OUTPUT_CONFIG = self.configs.get("output_config")

    async def background_rotation_check(self):
        while not self.exit_signal.is_set():
            self.rotate_log_path()
            await asyncio.sleep(15)

    def create_signals(self, handler):
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def exit_cleanup(self, num = None, frame = None):

        self.exit_signal.set()

        if hasattr(self, 'bg_task') and self.bg_task:
            self.bg_task.cancel()
            try:
                asyncio.get_event_loop().run_until_complete(self.bg_task)
            
            except asyncio.CancelledError as error:
                self.internal_log("An error occured when attempting a graceful exit", exception_traceback=error)

        self.loop.stop()
        self.loop.close()

        sys.exit(0)
 
    # file handling functions
 

    # log functions
 
    def build_log(self, message, error_level, exception_traceback = None):


        if error_level in self.ERROR_MAP:

            return ''.join([
                self.get_color(error_level) if self.LOG_COMPONENTS["color"] else "",
                self.get_timestamp() if self.LOG_COMPONENTS["timestamp"] else "",
                f"[{error_level}] " if self.LOG_COMPONENTS["level"] else "",
                f"{message} " if self.LOG_COMPONENTS["message"] else "",
                self.get_traceback(exception_traceback) if self.ERROR_MAP[error_level]["traceback"] and exception_traceback else ""
            ])


        return f"[{error_level}] {message}{f"\n{self.get_traceback(exception_traceback)}" if exception_traceback else ""}"

    def log(self, message, error_level, is_file = False, exception_traceback = None):

        message = self.build_log(message, error_level, exception_traceback)
        print(message)

        try:

            if is_file:
            
                self.log_to_file(message)

        except (FileNotFoundError, PermissionError) as error:
               
               self.internal_log("Encountered an error during logging", exception_traceback=error)

    def log_to_file(self, log):

        file_path = self.FILE_LOCATIONS["log_file_path"]

        try:

            with open (file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(log+"\n")

        except (PermissionError, FileNotFoundError) as error:
            self.internal_log(f"An error occured when appending log to file: {file_path}", exception_traceback=error)
    
    # log construction functions

    def get_color(self, error_level):
        return (self.ERROR_MAP.get(f"{error_level}", {}).get("color", "\033[0m")).encode().decode("unicode_escape")

    def get_timestamp(self):
        return f"[{datetime.now().strftime('%Y-%m-%d / %Hh-%Mm-%Ss')}]\n"
    
    def get_traceback(self, error):
        if error is None:
            self.internal_log("No error was provided")
            return ""
        
        if isinstance(error, type) and issubclass(error, Exception):
            error = error("No other information provided")

        if not hasattr(error, '__traceback__'):
            return "\nNo traceback provided"
        

        return "\n\033[0m" + ''.join(traceback.format_exception(None, error, error.__traceback__))
    
    # log level functions
    @staticmethod
    def internal_log(message,
                   exception_traceback = None,
                   ):
        

        print(f"\033[1;37m[INTERNAL] {message}")

        if exception_traceback:
            print(f"{traceback.print_exception(exception_traceback)}")  

class ConfigHandler:

    FALLBACK_CONFIGURATION = {

    "log_components": {
        "color": True,
        "timestamp": True,
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

        "log_rotation": True,
        "size_rotation": True,
        "max_byte_size": 5242880,
        "time_rotation": False,
        "max_day_length": 1

    },

    "output_config": {

        "console": True,
        "file": True

    }
}

    def __init__(self, config_path):

        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'Logger_primary_config.JSON')

        Logger.internal_log(f"Attempting to load configs from {config_path}")
        self.configs = self.get_config_map(config_path)
        Logger.internal_log("Initialising configuration file")

    def get_valid_config(self):

        self.validate_config_types(self.configs)
        self.validate_log_path()
        return self.configs

    def get_config_map(self, config_path):
         
        try:
            
            if os.path.exists(config_path):

                with open(config_path, 'r') as config:

                    Logger.internal_log("Custom config file successfully loaded")
                    return json.load(config)
            
            else:

                with open(config_path, 'w') as config_file:

                    Logger.internal_log("Creating config file with default configurations as 'Logger_primary_config'")
                    json.dump(ConfigHandler.FALLBACK_CONFIGURATION, config_file, indent=4)

                return ConfigHandler.FALLBACK_CONFIGURATION
            
        except (OSError, json.JSONDecodeError) as error:
            
            Logger.internal_log("Config file could not be accessed, or contains malformed data. Using fallback configuration.", exception_traceback=error)
            return ConfigHandler.FALLBACK_CONFIGURATION

    def validate_config_types(self, configs=None):

        if configs is None:
            configs = self.configs

        FALLBACK = ConfigHandler.FALLBACK_CONFIGURATION

        for key, value in configs.items():
            fallback = FALLBACK[key]

            if key not in FALLBACK:
                print("key")
                Logger.internal_log(f"Missing key {key} from configuration. Replacing with {fallback}")
                configs[key] = fallback

            if isinstance(value, dict) and isinstance(fallback, dict):
                
                for subkey, subvalue in value.items():

                  
                    if subkey not in fallback:
                        print("Subkey")
                        Logger.internal_log(f"Missing key {subkey} from configuration. Replacing with {FALLBACK[key][subkey]}")
                        configs[key][subkey] = FALLBACK[key][subkey]

                    subfallback = FALLBACK[key][subkey]

                    if isinstance(fallback[subkey], dict):

                        if not isinstance(subvalue, type(subfallback)):
                            Logger.internal_log(f"Encountered TypeError. Expected {type(subfallback)} but found {type(subvalue)}")
                            configs[key][subkey] = subfallback
                            continue

                continue

            if not isinstance(value, type(fallback)):
                Logger.internal_log(f"Encountered TypeError. Expected {type(fallback)} but found {type(value)}")
                value = fallback
                continue



    def validate_log_path(self):

        path = self.configs["file_locations"]["log_file_path"]

        if path == "{CURRENT_PATH}":
            path = f"{os.path.dirname(__file__)}\\log.txt"

        try:

            with open(path, 'a', encoding='utf-8'):

                self.configs["file_locations"]["log_file_path"] = path
                Logger.internal_log(f"Log file found or created. Using {path}.")

        except(FileNotFoundError, PermissionError) as error:

            self.config["output_config"]["file"] = False
            Logger.internal_log(f"Path [{path}] to the log file couldn't be found, or can't be accessed. Disabled file logging", exception_traceback=error)

class RotationHandler:

    def __init__(self, configs):
        self.configs = configs

    def check_rotation_condition(self, full_path, max_size, max_time):

        try:

            if os.path.getsize(full_path) >= max_size or datetime.now() - datetime.fromtimestamp(os.path.getctime(full_path)) >= timedelta(days=max_time):
                return True

        except (FileNotFoundError, PermissionError) as error:
            Logger.internal_log("An error occured whilst reading file size and creation time", exception_traceback=error)
            return False
    
    def rotate_log_path(self):

        Logger.internal_log("Running rotation check")

        if self.check_rotation_condition(self.FILE_LOCATIONS["log_file_path"], 
        self.LOG_ROTATION["max_byte_size"], 
        self.LOG_ROTATION["max_day_length"]
        ):
            
            try:
            
                self.full_rotation()

            except (FileNotFoundError, PermissionError) as error:

                Logger.internal_log("An error occured whilst attempting log rotation.", exception_traceback=error)
            
    def rename_rotating_log(self, log_file_path):
        archive_name = f"log_archive {datetime.now().strftime('%d_%m_%y %H_%M_%S')}_{random.randint(1000, 9999)}.txt"

        try:

            os.rename(log_file_path, archive_name)
            Logger.internal_log(f"Log file Archived as {archive_name}.\nArchived file size: {os.path.getsize(archive_name)}\nArchived file age: {os.path.getmtime(archive_name)}.")

        except (FileNotFoundError, PermissionError) as error:

            Logger.internal_log(f"Failed to rename log file at {log_file_path}", exception_traceback=error)

    def create_fresh_log(self, log_file_path):

        try:

            with open(log_file_path, 'a') as new_log_file:
                Logger.internal_log(f"Created new file as {new_log_file.name}")

        except PermissionError:

            Logger.internal_log(f"Permission to the new log file at {log_file_path} was denied")

    def full_rotation(self):

        is_success = True

        try:

            self.rename_rotating_log(self.configs["file_locations"]["log_file_path"])
            self.create_fresh_log(self.configs["file_locations"]["log_file_path"])

        except (FileNotFoundError, PermissionError) as error:

            is_success = False
            Logger.internal_log("An error occurred whilst rotating", exception_traceback=error)

        finally:

            Logger.internal_log(f"Rotation attempt complete. Success: {is_success}")



logger = Logger()

logger.log("Jamie Froom is a japseye", "WARNING")