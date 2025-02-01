import traceback
import os
import json
from datetime import datetime, timedelta

class Logger:

    FALLBACK_CONFIGURATION = {   

    "log_components" : {

    "color" : True,
    "timestamp" : True,
    "message" : True,
    "level" : True    

    },

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
            "traceback" : True
        }
    },

    "file_locations" : {

        "log_file_directory" : "{CURRENT_DIR}",
        "log_file_path" : "log.txt",
        "archive_folder" : "log_archives"

    },

    "log_rotation" : {

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
        """
        Initializes Logger class, loads the configuration file from the specified path. If config_path is None, the default 'Logger_primary_config.JSON' is used. 

        Args:
            config_path (str, optional): The path to the configuration file. If None, the default 'Logger_primary_config.JSON' will be loaded.
            If 'Logger_primary_config.JSON' doesn't exist, it will be created in the same directory as the current script with the fallback configuration.
            Missing or malformed data will default back to the fallback configuration.
        """

        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'Logger_primary_config.JSON')
            
        self.configs = self.get_config_map(config_path)

        if self.configs.get("file_locations").get("log_file_directory") == '{CURRENT_DIR}':
            self.configs["file_locations"]["log_file_directory"] = os.path.dirname(__file__)

        self.LOG_COMPONENTS = self.configs.get("log_components")
        self.ERROR_MAP = self.configs.get("error_map")
        self.FILE_LOCATIONS = self.configs.get("file_locations")
        self.LOG_ROTATION = self.configs.get("log_rotation")
        self.OUTPUT_CONFIG = self.configs.get("output_config")

    # config loading
 
    def get_config_map(self, config_path):
        """
        Returns the JSON object from a specified file path. If the file doesn't exist, a fallback configuration is returned and a new file is created with the fallback configuration.

        Args:
            config_path (str): Specifies a file path where the configuration file is stored.

        Returns:
            dict: A dictionary containing configuration settings.
        """
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


    def merge_configs(self):

        for key, fallback_value in Logger.FALLBACK_CONFIGURATION.items():
                if isinstance(fallback_value, dict):
                    self.configs.setdefault(key, {})
                    for nested_key, nested_value in fallback_value.items():
                            if not isinstance(self.configs[key].get(nested_key), dict):
                                self.configs[key][nested_key] = nested_value
                            else:
                                self.configs[key][nested_key].setdefault(nested_key, nested_value)
                else:
                    self.configs[key] = fallback_value

    # file handling functions
 
    def rotate_log_file(self
                     ):
        """
        Handles log rotation.
        """

        try:
            
            log_rotation = self.LOG_ROTATION.get("log_rotation", False)
            
            if log_rotation:
                
                time_rotation = self.LOG_ROTATION.get("time_rotation", False)
                size_rotation = self.LOG_ROTATION.get("size_rotation", False)

            
                if time_rotation:
                    self.check_time_rotation()

                if size_rotation:
                    self.check_size_rotation()

            else:
                
                self.internal_log("Log rotation is disabled in the configuration.")

        except (KeyError, OSError) as error:
            
            self.internal_log("Log rotation could not continue. Reason: ", exception_traceback=error)
        
    def check_size_rotation(self
                            ):
        """
        Rotates log file if it exceeds a specified size limit.

        Returns:
            bool: False if an error occured while rotating the log file or if rotation wasn't needed, True if log rotation occured successfully.
        """
        try:
            
            file_path = self.FILE_LOCATIONS.get("log_file_directory", None)
            file_name = self.FILE_LOCATIONS.get("log_file_path", None)
            max_size = self.LOG_ROTATION.get("max_byte_size", None)
            
            if file_path and file_name and max_size:
                
                full_path = os.path.join(file_path, file_name)
                
                if os.path.getsize(full_path) >= max_size:
                    
                    new_file_name = f"log_{str(datetime.now().strftime('%y%m%d_%H%M%S'))}.txt"
                    new_file_path = os.path.join(file_path, new_file_name)
                    os.rename(full_path, new_file_path)
                    
                    with open(new_file_path, 'w') as new_file:
                        
                        self.internal_log(f"Log file exceeded max size of {max_size}. Created new log file: {new_file_name}")

                    return True
                
            return False
                        
        except OSError as error:
            
            file_name = file_name if file_name else "Unknown file"
            self.internal_log(f"Size rotation could not be determined due to a file access error for {file_name} in {file_path}", exception_traceback=error)
            return False

    def check_time_rotation(self
                            ):
        """
        Rotates log file if it exceeds a specified time limit.

        Returns:
            bool: False if an error occured while rotating the log file or if rotation wasn't needed, True if log rotation occured successfully.
        """
        try:
            
            file_path = self.FILE_LOCATIONS.get("log_file_directory", None)
            file_name = self.FILE_LOCATIONS.get("log_file_path", None)
            rotate_days = self.LOG_ROTATION.get("max_day_length", None)
            
            if file_path and file_name and rotate_days:
                
                full_path = os.path.join(file_path, file_name)
                
                if datetime.now() - datetime.fromtimestamp(os.path.getctime(full_path)) >= timedelta(days=rotate_days):
                    
                    new_file_name = f"log_{str(datetime.now().strftime('%y%m%d_%H%M%S'))}.txt"
                    new_file_path = os.path.join(file_path, new_file_name)
                    os.rename(full_path, new_file_path)
                    
                    with open(new_file_path, 'w') as new_file:
                        
                        self.internal_log(f"Log file exceeded time limit of {rotate_days}. Created new log file: {new_file_name}")

                    return True
                
            return False
                        
        except OSError as error:
            
            file_name = file_name if file_name else "Unknown file"
            self.internal_log(f"Time rotation could not be determined due to a file access error for {file_name} in {file_path}", exception_traceback=error)
            return False

    # log functions
 
    def build_log(self, message, error_level, exception_message = None):
        string_components = {
            "color" : self.LOG_COMPONENTS["color"],
            "timestamp" : self.LOG_COMPONENTS["timestamp"],
            "level" : self.LOG_COMPONENTS["level"],
            "message" : self.LOG_COMPONENTS["message"],
            "traceback" : self.ERROR_MAP[error_level]["traceback"]
        }    

        component_functions = {
            "color" : self.get_color(error_level) if string_components["color"] else "",
            "timestamp" : self.get_timestamp() if string_components["timestamp"] else "",
            "level" : f"[{error_level}]" + " " if string_components["level"] else "",
            "message" : str(message) + " " if string_components["message"] else "",
            "traceback" : self.get_traceback(exception_message) if string_components["traceback"] and exception_message else ""
        }

        built_log = [component_functions[key] for key in component_functions if string_components[key]]

        print(''.join(built_log))
    
    def log_to_file(self, log):

        file_dir = self.FILE_LOCATIONS["log_file_directory"]
        file_path = self.FILE_LOCATIONS["log_file_path"]

        full_dir = os.path.join(file_dir, file_path)

        try:

            os.makedirs(file_dir, exist_ok=True)

            with open (full_dir, 'a', encoding='utf-8') as log_file:
                log_file.write(log+"\n")

        except OSError as error:
            self.internal_log(f"An error occured when appending log to file: {full_dir}", exception_message=error)
    
    # log construction functions

    def get_color(self, error_level):
        return (self.ERROR_MAP.get(f"{error_level}", {}).get("color", "\033[0m")).encode().decode("unicode_escape")

    def get_timestamp(self):
        return f"[{datetime.now().strftime("%Y-%m-%d / %Hh-%Mm-%Ss")}]\n"
    
    def get_traceback(self, error):
        if error is None:
            return ""
        
        if isinstance(error, type) and issubclass(error, Exception):
            error = error("No other information provided")
        

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
                 exception = None
                 ):
        """Prints an info level log to the console and optionally saves it to a file

        Args:
            message (str): The message logged to the console
            is_file (bool, optional): Determines whether the log is saved to a file. Defaults to False.
            exception (Exception, optional): (str, optional): Includes the exception to be logged (if any). Defaults to None.
        """
        try:
        
            log_string = self.build_log(message, "INFO", exception)
                
            if is_file:
                file_dir = self.configs.get("file_configs", {}).get("log_file_directory", "")
                file_path = self.configs.get("file_configs", {}).get("log_file_path", "")
                full_path = os.path.join(file_dir, file_path)

                os.makedirs(file_dir, exist_ok = True)

                with open(full_path, 'a') as log_file:
                    log_file.write(log_string + "\n")

        except OSError as error:
            
            self.internal_log("An error occurred during logging", exception_traceback = error)
		 
    def debug_log(self, 
                  message, 
                  is_file: bool = False, 
                  file_path = None, 
                  exception = None
                  ):
        """Prints a debug level log to the console and optionally saves it to a file

        Args:
            message (str): The message logged to the console
            is_file (bool, optional): Determines whether the log is saved to a file. Defaults to False.
            exception (Exception, optional): (str, optional): Includes the exception to be logged (if any). Defaults to None.
        """
        try:
        
            log_string = self.build_log(message, "DEBUG", exception)
                
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
        """Prints an error level log to the console and optionally saves it to a file

        Args:
            message (str): The message logged to the console
            is_file (bool, optional): Determines whether the log is saved to a file. Defaults to False.
            exception (Exception, optional): (str, optional): Includes the exception to be logged (if any). Defaults to None.
        """
        try:
        
            log_string = self.build_log(message, "ERROR", exception)
            
            if is_file and file_path:
                self.log_to_file(file_path, log_string)
            
        except Exception as error:
            
            self.internal_log("An error occurred during logging", exception_traceback = error)
		
    def warning_log(self, 
                    message, 
                    is_file: bool = False, 
                    file_path = None, 
                    exception = None
                    ):
        """Prints an warning level log to the console and optionally saves it to a file

        Args:
            message (str): The message logged to the console
            is_file (bool, optional): Determines whether the log is saved to a file. Defaults to False.
            exception (Exception, optional): (str, optional): Includes the exception to be logged (if any). Defaults to None.
        """
        try:
            
            log_string = self.build_log(message, "WARNING", exception)
            
            if is_file and file_path:
                self.log_to_file(file_path, log_string)
                
        except Exception as error:
            
            self.internal_log("An error occurred during logging", exception_traceback = error)
		
    def critical_log(self, 
                     message, 
                     is_file: bool = False, 
                     file_path = None, 
                     exception = None
                     ):
        """Prints an critical level log to the console and optionally saves it to a file

        Args:
            message (str): The message logged to the console
            is_file (bool, optional): Determines whether the log is saved to a file. Defaults to False.
            exception (Exception, optional): (str, optional): Includes the exception to be logged (if any). Defaults to None.
        """
        try:
        
            log_string = self.build_log(message, "CRITICAL", exception)
            
            if is_file and file_path:
                self.log_to_file(file_path, log_string)
        
        except OSError as error:
            
            self.internal_log("An error occurred during logging", exception_traceback = error)
                    
logger = Logger()

logger.info_log("Cunt", exception=ValueError)