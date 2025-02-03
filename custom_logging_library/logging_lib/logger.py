import traceback
import os
import json
import random
from datetime import datetime, timedelta
import asyncio
import signal
import sys

class Logger:

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
        "file": True,
        "debug_logs": True
    }
}
    # initialization function
    
    def __init__(self, 
                 config_path=None, 
                 ):

        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'Logger_primary_config.JSON')
            
        self.configs = self.get_config_map(config_path)

        self.validate_config_types()

        self.LOG_COMPONENTS = self.configs.get("log_components")
        self.ERROR_MAP = self.configs.get("error_map")
        self.FILE_LOCATIONS = self.configs.get("file_locations")
        self.LOG_ROTATION = self.configs.get("log_rotation")
        self.OUTPUT_CONFIG = self.configs.get("output_config")

        self.validate_log_path()

        self.exit_signal = asyncio.Event()

        self.create_signals(self.exit_cleanup)

        bg_loop = asyncio.get_event_loop()

        self.bg_task = bg_loop.create_task(self.background_rotation_check())

    def validate_log_path(self):

        path = self.FILE_LOCATIONS["log_file_path"]

        if path == "{CURRENT_PATH}":
            path = f"{os.path.dirname(__file__)}log.txt"

        try:

            with open(path, 'a', encoding='utf-8'):
                self.configs["file_locations"]["log_file_path"] = path
                return self.internal_log(f"Log file found or created. Using {path}.")

        except(FileNotFoundError, PermissionError) as error:

            self.OUTPUT_CONFIG["file"] = False
            self.internal_log(f"Path [{path}] to the log file couldn't be found, or can't be accessed. Disabled file logging", exception_message=error)

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
                self.internal_log("An error occured when attempting a graceful exit", exception_message=error)

        asyncio.get_event_loop().stop()

        sys.exit(0)

        

    # config loading
 
    def get_config_map(self, config_path):
         
        try:
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as config:
                    self.internal_log("Custom config file successfully loaded")
                    return json.load(config)
            
            else:
                with open(config_path, 'w') as config_file:
                    self.internal_log("Creating config file with default configurations as 'Logger_primary_config'", override=True)
                    json.dump(self.FALLBACK_CONFIGURATION, config_file, indent=4)
                return Logger.FALLBACK_CONFIGURATION
            
        except (OSError, json.JSONDecodeError) as error:
            
            self.internal_log("Config file could not be accessed, or contains malformed data. Using fallback configuration.", exception_traceback=error, override=True)
            return Logger.FALLBACK_CONFIGURATION

    def validate_config_types(self, configs=None):

        if configs is None:
            configs = self.configs

        for key, value in configs.items():

            fallback_key = Logger.FALLBACK_CONFIGURATION[key]

            if fallback_key is None:
                self.internal_log(f"Key {key} is missing from configuration.")
                continue

            if isinstance(fallback_key, dict):
                if isinstance(key, dict):
                    self.validate_config_types(value)
                    continue

            if not isinstance(value, type(fallback_key)):
                self.internal_log(f"Encountered type mismatch at {key} with value {value}. Expected {type(fallback_key)} but found {type(value)}.")
                configs[key] = fallback_key

    # file handling functions
 
    def check_rotation_condition(self, full_path, max_size, max_time):

            if os.path.getsize(full_path) >= max_size or datetime.now() - datetime.fromtimestamp(os.path.getctime(full_path)) >= timedelta(days=max_time):
                return True
        
            return False
    
    def rotate_log_path(self):

        self.internal_log("Running rotation check")

        if self.check_rotation_condition(self.FILE_LOCATIONS["log_file_path"], 
                                         self.LOG_ROTATION["max_byte_size"], 
                                         self.LOG_ROTATION["max_day_length"]
                                         ):
            
            try:
            
                log_file_abspath = self.FILE_LOCATIONS["log_file_path"]
                
                self.rename_rotating_log(log_file_abspath)
                
                self.create_fresh_log(log_file_abspath)

            except OSError as error:
                self.internal_log("An error occured whilst attempting log rotation.", exception_message=error)
            
    def rename_rotating_log(self, log_file_path):
        archive_name = f'log_archive {datetime.now().strftime("%d_%m_%y %H_%M_%S")}_{random.randint(1000, 9999)}.txt'


        try:

            with open(log_file_path, 'a', encoding='utf-8'):
                    
                os.rename(log_file_path, archive_name)
                self.internal_log(f"Log file created. Archived as {archive_name}. Archived file size: {os.path.getsize(archive_name)}, Archived file age: {os.path.getmtime(archive_name)}.")

        except (FileNotFoundError, PermissionError) as error:

            self.internal_log("Failed to rename full or old log file", exception_message=error)

    def create_fresh_log(self, log_file_path):

        try:

            with open(log_file_path, 'a') as new_log_file:
                self.internal_log(f"Created new file as {new_log_file}")

        except (FileNotFoundError, PermissionError) as error:

            self.internal_log(f"A new file couldn't be created at {log_file_path}.", exception_message=error)

    # log functions
 
    def build_log(self, message, error_level, exception_message = None):

        built_log = ''.join({
            "color": self.get_color(error_level) if self.LOG_COMPONENTS["color"] else "",
            "timestamp": self.get_timestamp() if self.LOG_COMPONENTS["timestamp"] else "",
            "level": f"[{error_level}] " if self.LOG_COMPONENTS["level"] else "",
            "message": f"{message} " if self.LOG_COMPONENTS["message"] else "",
            "traceback": self.get_traceback(exception_message) if self.ERROR_MAP[error_level]["traceback"] and exception_message else ""
        }.values())

        return built_log
    
    def log(self, message, error_level, is_file = False, exception_message = None):

        try:

            message = self.build_log(message, error_level, exception_message)
            print(message)

            if is_file:
            
                self.log_to_file(message)

        except (Exception, OSError) as error:
               
               self.internal_log("Encountered an error during logging", exception_message=error)

    def log_to_file(self, log):

        file_path = self.FILE_LOCATIONS["log_file_path"]


        try:

            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open (file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(log+"\n")

        except OSError as error:
            self.internal_log(f"An error occured when appending log to file: {file_path}", exception_message=error)
    
    # log construction functions

    def get_color(self, error_level):
        return (self.ERROR_MAP.get(f"{error_level}", {}).get("color", "\033[0m")).encode().decode("unicode_escape")

    def get_timestamp(self):
        return f"[{datetime.now().strftime("%Y-%m-%d / %Hh-%Mm-%Ss")}]\n"
    
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
    
    def internal_log(self,
                   message,
                   exception_message = None,
                   override = False
                   ):
        """Prints an internal log for debugging and error tracing within the library

        Args:
            message (str): The message logged to the console.
            exception_traceback (str, optional): Includes the exception to be logged (if any). Defaults to None.
            override (bool, optional): Determines whether the log should be displayed despite config settings. Defaults to False.
        """
        DEBUG_LOGS = getattr(self,"OUTPUT_CONFIG", {}).get("debug_logs", True)
        
        if override or DEBUG_LOGS:
            print(f"\033[1;37m[INTERNAL] {message}")
            if exception_message:
                print(f"{self.get_traceback(exception_message)}")
 
    def info_log(self, 
                 message, 
                 is_file: bool = False, 
                 exception: Exception = None
                 ):
        """Prints an info level log to the console and optionally saves it to a file

        Args:
            message (str): The message logged to the console
            is_file (bool, optional): Determines whether the log is saved to a file. Defaults to False.
            exception (Exception, optional): (str, optional): Includes the exception to be logged (if any). Defaults to None.
        """
        
        self.log(message, "INFO", is_file, exception)
                
    def debug_log(self, 
                  message, 
                  is_file: bool = False, 
                  exception = None
                  ):
        """Prints a debug level log to the console and optionally saves it to a file

        Args:
            message (str): The message logged to the console
            is_file (bool, optional): Determines whether the log is saved to a file. Defaults to False.
            exception (Exception, optional): (str, optional): Includes the exception to be logged (if any). Defaults to None.
        """
        
        self.log(message, "DEBUG", is_file, exception)
                

    def error_log(self, 
                  message, 
                  is_file: bool = False,  
                  exception = None
                  ):
        """Prints an error level log to the console and optionally saves it to a file

        Args:
            message (str): The message logged to the console
            is_file (bool, optional): Determines whether the log is saved to a file. Defaults to False.
            exception (Exception, optional): (str, optional): Includes the exception to be logged (if any). Defaults to None.
        """
        
        self.log(message, "ERROR", is_file, exception)
                

    def warning_log(self, 
                    message, 
                    is_file: bool = False, 
                    exception = None
                    ):
        """Prints an warning level log to the console and optionally saves it to a file

        Args:
            message (str): The message logged to the console
            is_file (bool, optional): Determines whether the log is saved to a file. Defaults to False.
            exception (Exception, optional): (str, optional): Includes the exception to be logged (if any). Defaults to None.
        """
        
        self.log(message, "WARNING", is_file, exception)
                
    def critical_log(self, 
                     message, 
                     is_file: bool = False,  
                     exception = None
                     ):
        """Prints an critical level log to the console and optionally saves it to a file

        Args:
            message (str): The message logged to the console
            is_file (bool, optional): Determines whether the log is saved to a file. Defaults to False.
            exception (Exception, optional): (str, optional): Includes the exception to be logged (if any). Defaults to None.
        """
        
        self.log(message, "CRITICAL", is_file, exception)
                

logger = Logger()

logger.info_log("CUMCUMCUMCUM", is_file=True)