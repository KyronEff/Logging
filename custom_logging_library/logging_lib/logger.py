import traceback
import os
import json
from datetime import datetime, timedelta

class Logger:
    
    FALLBACK_CONFIGURATION = {   
    "log_format" : {
    "color" : True,
    "timestamp" : True,
    "message" : True,
    "level" : True        
    },

<<<<<<< Updated upstream
    "error_map" : {
        
        "INFO" : {
            "color" : "\\033[0;34m",
            "level" : "INFO", 
            "traceback" : False
        },
       
        "DEBUG" : {
            "color" : "\\033[0;35m", 
            "level" : "DEBUG",
            "traceback" : True
=======
 # initialization function
    _compiler = None
    _output = None

    def __init__(self, config_path=None):

        self.configs = HandleConfigs(config_path).get_valid_config()

        if not Logger._compiler:
            self._compiler = CompileLog(
                self.configs["error_map"], self.configs["log_components"])
        if not Logger._output:
            self._output = HandleOutput(self.configs["output_configs"])

    def log(self, message, level, exception_traceback=None):

        message = self._compiler.build_log(message, level, exception_traceback)
        self._output.handle_log_output(
            message, self.configs["file_locations"]["log_file_path"])


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

        return f"[{datetime.now().strftime(log_components["timestamp_format"])}]\n"

    @staticmethod
    def get_traceback(error):

        if error is None:

            HandleOutput.log_internal_message("No error was provided")
            return ""

        if isinstance(error, type) and issubclass(error, Exception):

            error = error("No other information provided")

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

            print(
                f"{traceback.format_exception(None, exception_traceback, exception_traceback.__traceback__)}")


class HandleConfigs:

    FALLBACK_CONFIGURATION = {

        "log_components": {
            "color": True,
            "timestamp": True,
            "timestamp_format": r"%Y-%m-%d / %Hh-%Mm-%Ss",
            "message": True,
            "level": True
>>>>>>> Stashed changes
        },

        "ERROR" : {
            "color" : "\\033[0;31m", 
            "level" : "ERROR", 
            "traceback" : False
        }, 

        "WARNING" : {
            "color" : "\\033[1;33m", 
            "level" : "WARNING", 
            "traceback" : True
        },

        "CRITICAL" : {
            "color" : "\\033[1;35m", 
            "level" : "CRITICAL", 
            "traceback" : True}
    },

    "file_configs" : {
        "log_file_directory" : "__file__",
        "log_file_path" : "log.txt",
        "archive_folder" : "log_archives"
    },

    "rotation_configs" : {
        "log_rotation" : True,
        "size_rotation" : True,
        "max_byte_size" : 5242880,
        "time_rotation" : False,
        "max_day_length" : 1
    },

    "output_config" : {
        "console" : True,
        "file" : True,
        "debug_logs" : True
    }
}
    # initialization function
    
    def __init__(self, 
                 config_path=None, 
                 ):
        
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'Logger_primary_config.JSON')
            
        self.configs = self.get_config_map(config_path)

    # config loading
 
    def get_config_map(self, config_path):
        
        try:
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as config:
                    self.general_log("Custom config file successfully loaded")
                    return json.load(config)
            
            else:
                with open(config_path, 'w') as config_file:
                    self.general_log("Creating config file with default configurations as 'Logger_primary_config'", override=True)
                    json.dump(self.FALLBACK_CONFIGURATION, config_file, indent=4)
                return Logger.FALLBACK_CONFIGURATION
            
        except (OSError, json.JSONDecodeError) as error:
            
            self.general_log("Config file could not be accessed, or contains malformed data. Using fallback configuration.", exception_traceback=error, override=True)
            return Logger.FALLBACK_CONFIGURATION

    # file handling functions
 
    def log_to_file(self, 
                    file_path, 
                    log
                    ):
        
        try:
            
            with open(file_path, 'a') as file:
                file.write(log + '\n')
                
        except OSError as error:
            
            self.general_log("Assigned file could not be accessed.", exception_traceback=error, override=True)
            return None

    def log_rotation(self
                     ):
        
        try:
            
            rotation_config = self.configs.get("rotation_configs", {})
            
            time_rotation = rotation_config.get("time_rotation", False)
            size_rotation = rotation_config.get("size_rotation", False)
            log_rotation = rotation_config.get("log_rotation", False)
            
            if log_rotation:
                if time_rotation:
                    self.check_time_rotation()
                if size_rotation:
                    self.check_size_rotation()
        except OSError as error:
            self.general_log("Log rotation could not continue and is unavailable", exception_traceback=error)
        
    def check_size_rotation(self
                            ):
        
        try:
            
            rotation_configs = self.configs.get("rotation_configs", {})
            file_configs = self.configs.get("file_configs", {})
            
            file_path = file_configs.get("log_file_directory", None)
            file_name = file_configs.get("log_file_path", None)
            max_size = rotation_configs.get("max_byte_size", None)
            
            if file_path and file_name and max_size:
                
                full_path = os.path.join(file_path, file_name)
                
                if os.path.getsize(full_path) >= max_size:
                    
                    new_file_name = f"log_{str(datetime.now().strftime('%y%m%d_%H%M%S'))}.txt"
                    new_file_path = os.path.join(file_path, new_file_name)
                    os.rename(full_path, new_file_path)
                    
                    with open(new_file_path, 'w') as new_file:
                        
                        self.info_log(f"Log file exceeded max size. Created new log file: {new_file}")
                        
        except OSError as error:
            
            self.general_log("Size rotation could not be determined and is unavailable", exception_traceback=error)
            return False

    def check_time_rotation(self
                            ):
        
        try:
            
            rotation_configs = self.configs.get("rotation_configs", {})
            file_configs = self.configs.get("file_configs", {})
            
            file_path = file_configs.get("log_file_directory", None)
            file_name = file_configs.get("log_file_path", None)
            time_length = rotation_configs.get("max_day_length", None)
            
            if file_path and file_name and time_length:
                
                full_path = os.path.join(file_path, file_name)
                
                if datetime.now() - datetime.fromtimestamp(os.path.getctime(full_path)) >= timedelta(days=time_length):
                    
                    new_file_name = f"log_{str(datetime.now().strftime('%y%m%d_%H%M%S'))}.txt"
                    new_file_path = os.path.join(file_path, new_file_name)
                    os.rename(full_path, new_file_path)
                    
                    with open(new_file_path, 'w') as new_file:
                        
                        self.info_log(f"Log file exceeded time limit. Created new log file: {new_file}")
                        
        except OSError as error:
            
            self.general_log("Time rotation could not be determined and is unavailable", exception_traceback=error)
            return False

    # log function
 
    def log(self,  
            error_message,
            error_level,
            exception = None
            ):
        
        log_format = self.configs.get("log_format", {})
        
        string_components = {
            'color' : log_format.get("color", False),
            'timestamp' : log_format.get("timestamp", False),
            'level' : log_format.get("level", False),
            'message' : log_format.get("message", False)
        }
        
        log_string = []
        
        if string_components['color']:
            ansi_escape = (self.configs.get("error_map", {}).get(f"{error_level}", {}).get("color", "\033[0m")).encode().decode("unicode_escape")
            log_string.append(ansi_escape)
            
        if string_components['timestamp']:
            log_string.append(f"[{datetime.now()}]\n")
            
        if string_components['level']:
            log_string.append(f"[{error_level}] ")
            
        if string_components['message']:
            log_string.append(error_message)
            
        if string_components['color']:
            log_string.append("\033[0m")
            
        if exception and self.configs.get("error_map", {}).get(error_level, False).get("traceback", False):
            log_string.append(f"\nTraceback: {traceback.format_exc()}")
            
        if self.configs.get("output_config", False).get("console", False):
            print(''.join(log_string))
            
        return ''.join(log_string)

    # log level functions
    
    def general_log(self,
                   message,
                   exception_traceback = None,
                   override = False
                   ):
        
        if not hasattr(self, 'configs') or override and not self.configs.get("output_config", True).get("debug_logs", True):
            print(f"\033[1;37m[GENERAL] {message}")
            if exception_traceback:
                print(f"\033[0mTraceback: {exception_traceback}")
 
    def info_log(self, 
                 message, 
                 is_file: bool = False, 
                 exception = None
                 ):
        
        try:
        
            log_string = self.log(message, 'INFO', exception)
                
            if is_file:
                file_dir = self.configs.get("file_configs", {}).get("log_file_directory", "")
                file_path = self.configs.get("file_configs", {}).get("log_file_path", "")
                full_path = os.path.join(file_dir, file_path)

                os.makedirs(file_dir, exist_ok = True)

                with open(full_path, 'a') as log_file:
                    log_file.write(log_string + "\n")

        except OSError as error:
            
            self.general_log("An error occurred during logging", exception_traceback = error)
		 
    def debug_log(self, 
                  message, 
                  is_file: bool = False, 
                  file_path = None, 
                  exception = None
                  ):
        
        try:
        
            log_string = self.log(message, 'DEBUG', exception)
                
            if is_file and file_path:
                self.log_to_file(file_path, log_string)
            
        except Exception as error:
            
            self.critical_log("Debug log is invalid. Consider checking your config file", exception_traceback = error)
        	
    def error_log(self, 
                  message, 
                  is_file: bool = False, 
                  file_path = None, 
                  exception = None
                  ):
        
        try:
        
            log_string = self.log(message, 'ERROR', exception)
            
            if is_file and file_path:
                self.log_to_file(file_path, log_string)
            
        except Exception as error:
            
            self.general_log("An error occurred during logging", exception_traceback = error)
		
    def warning_log(self, 
                    message, 
                    is_file: bool = False, 
                    file_path = None, 
                    exception = None
                    ):
        
        try:
            
            log_string = self.log(message, 'WARNING', exception)
            
            if is_file and file_path:
                self.log_to_file(file_path, log_string)
                
        except Exception as error:
            
            self.general_log("An error occurred during logging", exception_traceback = error)
		
    def critical_log(self, 
                     message, 
                     is_file: bool = False, 
                     file_path = None, 
                     exception = None
                     ):

        try:
<<<<<<< Updated upstream
        
            log_string = self.log(message, 'CRITICAL', exception)
            
            if is_file and file_path:
                self.log_to_file(file_path, log_string)
        
        except OSError as error:
            
            self.general_log("An error occurred during logging", exception_traceback = error)
                    
logger = Logger()
=======

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
                print("key")
                HandleOutput.log_internal_message(
                    "Specified config uses malformed or corrupted data. Using Fallback")
                self.configs = FALLBACK
                return

            fallback = FALLBACK[key]

            if isinstance(value, dict) and isinstance(fallback, dict):

                for subkey, subvalue in value.items():

                    if subkey not in fallback:
                        print("Subkey")
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
            path = f"{os.path.dirname(__file__)}\\log.txt"

        try:

            with open(path, 'a', encoding='utf-8'):

                self.configs["file_locations"]["log_file_path"] = path
                HandleOutput.log_internal_message(
                    f"Log file found or created. Using {path}.")

        except (FileNotFoundError, PermissionError) as error:

            self.configs["output_config"]["file"] = False
            self.configs["log_rotation_configs"]["log_rotation"] = False
            HandleOutput.log_internal_message(
                f"Path [{path}] to the log file couldn't be found, or can't be accessed. Disabled file rotation and logging", exception_traceback=error)


class HandleRotation:

    def __init__(self, configs):
        self.configs = configs

    def check_rotation_condition(self, full_path, max_size, max_time):

        if os.path.getsize(full_path) >= max_size or datetime.now() - datetime.fromtimestamp(os.path.getctime(full_path)) >= timedelta(days=max_time):
            return True
        return False

    def rotate_log_path(self):

        HandleOutput.log_internal_message("Running rotation check")

        if self.check_rotation_condition(self.FILE_LOCATIONS["log_file_path"],
                                         self.LOG_ROTATION["max_byte_size"],
                                         self.LOG_ROTATION["max_day_length"]
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

        self.rename_rotating_log(
            self.configs["file_locations"]["log_file_path"])
        self.create_fresh_log(self.configs["file_locations"]["log_file_path"])


logger = Logger()

logger.log("Test\nNewline", "TEST")
>>>>>>> Stashed changes
