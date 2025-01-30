import traceback, os, json
from datetime import datetime, timedelta

class Logger:
    
    FALLBACK_CONFIGURATION = {
          
    "log_format" : {
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
            "color" : "\\033[0;32m", 
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

    "file_config" : {
        
        "log_file" : "log.txt",
        "archive_folder" : "log_archives",
        "log_rotation" : True,
        "max_byte_size" : 5242880
        
    },

    "output_config" : {
        
        "console" : True,
        "file" : True
        
    }
}
    
    # initialization function
    
    def __init__(self, 
                 configs='logging_lib\\Configs\\primary_config.JSON', 
                 default_configs='logging_lib\\Configs\\fallback_config.JSON'
                 ):
        self.configs = self.get_configs(configs, default_configs)

    # config loading
 
    def get_configs(self, 
                    primary_config_obj, 
                    ):

        config = primary_config_obj
              
        loaded_config = self.load_config(config)
        if loaded_config:
            return loaded_config
        self.debug_log(f"Failed to load {config}.")
                
        raise RuntimeError("Both primary and fallback configuration files failed to load")
        
    def load_config(self,
                    config_path):
            
            try:
                
                with open(config_path, 'r') as config_file:
                    return json.load(config_file)
            
            except (OSError, json.JSONDecodeError) as error:
            
                self.debug_log(f"Failed to open config file from {config_path}", exception=error)
                return None    
            
    def validate_keys(self, 
                      config
                      ):
        
        required_keys = ['color', 'timestamp', 'message', 'level']
        
        try:
            
            if not isinstance(config["log_format"], dict):
                raise TypeError
            
            for key in required_keys:
                if key not in config["log_format"]:
                    raise KeyError(key)
                
            return True
        
        except KeyError as error:
            
            self.debug_log(f"Key {error.args[0]} could not be found in configuration file", exception=error)
            return False
        
        except TypeError as error:
            
            self.debug_log(f"Invalid typing for 'log_format': Expected [dict] type", exception=error)
            return False
     
    #file handling functions
 
    def log_to_file(self, 
                    file_name, 
                    log
                    ):
        
        try:
            
            with open(file_name, 'a') as file:
                file.write(log + '\n')
                
        except OSError as error:
            
            self.debug_log(f"Assigned file could not be accessed.", exception=error)
            return None

    def log_rotation(self
                     ):
        
        try:
            time_rotation = self.configs.get("time_rotation")
            size_rotation = self.configs.get("size_rotation")
            log_rotation = self.configs.get("log_rotation")
            
            if log_rotation:
                if time_rotation:
                    self.check_time_rotation()
                if size_rotation:
                    self.check_size_rotation()
        except OSError as error:
            self.debug_log("Log rotation could not continue and is unavailable", exception=error)
        
    def check_size_rotation(self
                            ):
        
        try:
            
            file_path = self.configs.get("log_file_directory", None)
            file_name = self.configs.get("log_file_name", None)
            max_size = self.configs.get("max_byte_size", None)
            
            if file_path and file_name and max_size:
                
                full_path = os.path.join(file_path, file_name)
                
                if os.path.getsize(full_path) >= max_size:
                    
                    new_file_name = f"log_{str(datetime.now().strftime('%y%m%d_%H%M%S'))}.txt"
                    new_file_path = os.path.join(file_path, new_file_name)
                    os.rename(full_path, new_file_path)
                    
                    with open(new_file_path, 'w') as new_file:
                        
                        self.info_log("Log file exceeded max size. Created new log file")
                        
        except OSError as error:
            
            self.debug_log("Size rotation could not be determined and is unavailable", exception=error)
            return False

    def check_time_rotation(self
                            ):
        
        try:
            
            file_path = self.configs.get("log_file_directory", None)
            file_name = self.configs.get("log_file_name", None)
            time_length = self.configs.get("max_day_length", None)
            
            if file_path and file_name and time_length:
                
                full_path = os.path.join(file_path, file_name)
                
                if datetime.now() - datetime.fromtimestamp(os.path.getctime(full_path)) >= timedelta(days=time_length):
                    
                    new_file_name = f"log_{str(datetime.now().strftime('%y%m%d_%H%M%S'))}.txt"
                    new_file_path = os.path.join(file_path, new_file_name)
                    os.rename(full_path, new_file_path)
                    
                    with open(new_file_path, 'w') as new_file:
                        
                        self.info_log("Log file exceeded time limit. Created new log file")
                        
        except OSError as error:
            
            self.debug_log("Time rotation could not be determined and is unavailable", exception=error)
            return False

    # log function
 
    def log(self,  
            error_message,
            error_level,
            exception =None
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
            
        log_string.append("\033[0m")
            
        if exception and self.configs.get("error_map", False).get(error_level, False).get("traceback", False):
            log_string.append(f"\nTraceback: {traceback.format_exc()}")
            
        if self.configs.get("output_config", False).get("console", False):
            print(''.join(log_string))
            
        return ''.join(log_string)

    # log level functions 
 
    def info_log(self, 
                 message, 
                 is_file: bool =False, 
                 file_path =None, 
                 exception: bool =False
                 ):
        
        try:
        
            log_string = self.log(message, 'INFO', exception)
                
            if is_file and file_path:
                self.log_to_file(file_path, log_string)
            
        except Exception as error:
            
            self.debug_log("An error occurred during logging", exception =error)
		 
    def debug_log(self, 
                  message, 
                  is_file: bool =False, 
                  file_path =None, 
                  exception: bool =False
                  ):
        
        try:
        
            log_string = self.log(message, 'DEBUG', exception)
                
            if is_file and file_path:
                self.log_to_file(file_path, log_string)
            
        except Exception as error:
            
            self.critical_log("Debug log is invalid. Consider checking your config file", exception =error)
        	
    def error_log(self, 
                  message, 
                  is_file: bool =False, 
                  file_path =None, 
                  exception: bool =False
                  ):
        
        try:
        
            log_string = self.log(message, 'ERROR', exception)
            
            if is_file and file_path:
                self.log_to_file(file_path, log_string)
            
        except Exception as error:
            
            self.debug_log("An error occurred during logging", exception =error)
		
    def warning_log(self, 
                    message, 
                    is_file: bool =False, 
                    file_path =None, 
                    exception: bool =False
                    ):
        
        try:
            
            log_string = self.log(message, 'WARNING', exception)
            
            if is_file and file_path:
                self.log_to_file(file_path, log_string)
                
        except Exception as error:
            
            self.debug_log("An error occurred during logging", exception =error)
		
    def critical_log(self, 
                     message, 
                     is_file: bool =False, 
                     file_path =None, 
                     exception =None
                     ):
        
        try:
        
            log_string = self.log(message, 'CRITICAL', exception)
            
            if is_file and file_path:
                self.log_to_file(file_path, log_string)
        
        except Exception as error:
            
            self.debug_log("An error occurred during logging", exception =error)
                    
logger = Logger()