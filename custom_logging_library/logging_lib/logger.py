import traceback, os, json
from datetime import datetime

class Logger:
    def __init__(self, configs='logging_lib\\Configs\\config.JSON', default_configs=r'logging_lib\\Configs\\default_config.JSON'):
	# Function to initialize log configs
        self.configs = self.get_configs(configs, default_configs)
	
    def get_configs(self, config_obj, default_config_obj):
        config = None
        try:
            if config_obj:
                with open(config_obj, 'r') as file:
                    config = json.load(file)
                if self.validate_keys(config):
                    return config
        except (FileNotFoundError, PermissionError, IsADirectoryError, json.JSONDecodeError, KeyError, TypeError) as error:
            self.info_log(f"An error occured whilst loading the configuration file. Falling back to default configuration. {error}", exception=True)
        try:
            with open(default_config_obj, 'r') as file:
                config = json.load(file)
            if self.validate_keys(config):
                self.info_log("Default configuration file loaded successfully.")
                return config
        except (json.JSONDecodeError, FileNotFoundError) as error:
            self.critical_log(f"No valid config file could be loaded. {error}", exception=True)
            raise RuntimeError("No valid config file could be loaded.")
        raise RuntimeError("Neither configuration file is valid")
		
    def validate_keys(self, config):
        required_keys = ['color', 'timestamp', 'message', 'level']
        if not isinstance(config["log_format"], dict):
            raise TypeError("Required keys could not be found or is not a dictionary")
        for key in required_keys:
            if key not in config["log_format"]:
                raise KeyError(f"{key} could not be found in config file")
        return True
		

    def log(self,  
        error_message,
        error_level,
        exception: bool =False):
        log_string = []
        if self.configs.get("log_format", False).get("color", False):
            ansi_escape = (self.configs.get("error_map", {}).get(f"{error_level}", {}).get("color", "\033[0m")).encode().decode("unicode_escape")
            log_string.append(ansi_escape)
        if self.configs.get("log_format", False).get("timestamp", False):
            log_string.append(f"{datetime.now()}\n")
        if self.configs.get("log_format", False).get("level", False):
            log_string.append(error_level + " ")
        if self.configs.get("log_format", False).get("message", False):
            log_string.append(error_message)
        if exception:
            print(f"Traceback: {traceback.format_exc()}")
        
        log_string.append("\033[0m")
        if self.configs.get("output_config", False).get("console", False):
            print(''.join(log_string))
        return ''.join(log_string)
	
    def log_to_file(self, file_name, log):
        try:
            with open(file_name, 'a') as file:
                file.write(log + '\n')
        except Exception as error:
            self.error_log("Passed file could not be located. Aborting write.", Exception=True)
			
    def info_log(self, message, is_file: bool =False, file =None, exception: bool =False):
        log_string = self.log(message, 'INFO', exception)
        if is_file and file:
            self.log_to_file(file, log_string)
		
    def debug_log(self, message, is_file: bool =False, file =None, exception: bool =False):
        log_string = self.log(message, 'DEBUG', exception)
        if is_file and file:
            self.log_to_file(file, log_string)
			
    def error_log(self, message, is_file: bool =False, file =None, exception: bool =False):
        log_string = self.log(message, 'ERROR', exception)
        if is_file and file:
            self.log_to_file(file, log_string)
			
    def warning_log(self, message, is_file: bool =False, file =None, exception: bool =False):
        log_string = self.log(message, 'WARNING', exception)
        if is_file and file:
            self.log_to_file(file, log_string)
		
    def critical_log(self, message, is_file: bool =False, file =None, exception: bool =False):
        log_string = self.log(message, 'CRITICAL', exception)
        if is_file and file:
            self.log_to_file(file, log_string)
            
logger = Logger()


logger.critical_log("This is an error message that took way too long to program", is_file=True, file='log.txt')