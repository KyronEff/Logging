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

    # file handling functions
 
    def log_to_file(self, 
                    file_path, 
                    log
                    ):
        
        try:
            
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write(log + '\n')
            return True
                
        except OSError as error:
            
            self.internal_log("Assigned file could not be accessed.", exception_traceback=error, override=True)
            return False

    def rotate_log_file(self
                     ):
        
        try:
            
            time_rotation = self.LOG_ROTATION.get("time_rotation", False)
            size_rotation = self.LOG_ROTATION.get("size_rotation", False)
            log_rotation = self.LOG_ROTATION.get("log_rotation", False)
            
            if log_rotation:
                if time_rotation:
                    self.check_time_rotation()
                if size_rotation:
                    self.check_size_rotation()
        except OSError as error:
            self.internal_log("Log rotation could not continue and is unavailable", exception_traceback=error)
        
    def check_size_rotation(self
                            ):
        
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
                        
                        self.info_log(f"Log file exceeded max size. Created new log file: {new_file}")
                        
        except OSError as error:
            
            self.internal_log("Size rotation could not be determined and is unavailable", exception_traceback=error)
            return False

    def check_time_rotation(self
                            ):
        
        try:
            
            file_path = self.FILE_LOCATIONS.get("log_file_directory", None)
            file_name = self.FILE_LOCATIONS.get("log_file_path", None)
            time_length = self.LOG_ROTATION.get("max_day_length", None)
            
            if file_path and file_name and time_length:
                
                full_path = os.path.join(file_path, file_name)
                
                if datetime.now() - datetime.fromtimestamp(os.path.getctime(full_path)) >= timedelta(days=time_length):
                    
                    new_file_name = f"log_{str(datetime.now().strftime('%y%m%d_%H%M%S'))}.txt"
                    new_file_path = os.path.join(file_path, new_file_name)
                    os.rename(full_path, new_file_path)
                    
                    with open(new_file_path, 'w') as new_file:
                        
                        self.info_log(f"Log file exceeded time limit. Created new log file: {new_file}")
                        
        except OSError as error:
            
            self.internal_log("Time rotation could not be determined and is unavailable", exception_traceback=error)
            return False

    # log function
 
    def log(self,  
            error_message,
            error_level,
            exception = None
            ):
        
        log_format = self.LOG_COMPONENTS
        
        string_components = {
            'color' : log_format.get("color", False),
            'timestamp' : log_format.get("timestamp", False),
            'level' : log_format.get("level", False),
            'message' : log_format.get("message", False)
        }
        
        log_string = []
        
        if string_components['color']:
            ansi_escape = (self.ERROR_MAP.get(f"{error_level}", {}).get("color", "\033[0m")).encode().decode("unicode_escape")
            log_string.append(ansi_escape)
            
        if string_components['timestamp']:
            log_string.append(f"[{datetime.now()}]\n")
            
        if string_components['level']:
            log_string.append(f"[{error_level}] ")
            
        if string_components['message']:
            log_string.append(str(error_message))
            
        if string_components['color']:
            log_string.append("\033[0m")
            
        if exception is not None and self.configs.get("error_map", {}).get(error_level, False).get("traceback", False):
            log_string.append(f"\nTraceback: {traceback.format_exc()}")
            
        if self.configs.get("output_config", False).get("console", False):
            print(''.join(log_string))
            
        return ''.join(log_string)

    # log level functions
    
    def internal_log(self,
                   message,
                   exception_traceback = None,
                   override = False
                   ):

        DEBUG_LOGS = getattr(self,"OUTPUT_CONFIG", {}).get("debug_logs", True)
        
        if override or DEBUG_LOGS:
            print(f"\033[1;37m[INTERNAL] {message}")
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
            
            self.internal_log("An error occurred during logging", exception_traceback = error)
		 
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
            
            self.internal_log("An error occurred during logging", exception_traceback = error)
		
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
            
            self.internal_log("An error occurred during logging", exception_traceback = error)
		
    def critical_log(self, 
                     message, 
                     is_file: bool = False, 
                     file_path = None, 
                     exception = None
                     ):

        try:
        
            log_string = self.log(message, 'CRITICAL', exception)
            
            if is_file and file_path:
                self.log_to_file(file_path, log_string)
        
        except OSError as error:
            
            self.internal_log("An error occurred during logging", exception_traceback = error)
                    
logger = Logger()