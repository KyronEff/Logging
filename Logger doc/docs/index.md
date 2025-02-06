# logger Documentation

## Overview

logger is a lightweight library for consistent and formatted logging. logger has features like log file rotation for extended use, error levels for unique errors, and an almost fully configurable setup.

## Installation

logger can be installed via `pip`

`bash` <br>
`pip install logger`

Built with `Python v3.13.1 64bit`

## Basic Usage

**Import**

`from logger import Logger`

**Initializing a logger instance**

`logger = Logger()`

When initializing logger, you can pass a config file

`logger = Logger("my_logger_config.JSON")`

**Printing a log**

*Terminal*

`logger.log("Log message", "LOG LEVEL")`

--> `[LOG LEVEL] Log message`

*File*

`logger.log("Log message", "LOG LEVEL", is_file=True)`

--> In log file: `[LOG LEVEL] Log message`

The file logs are written to is in the configs as `log_file_path`. Prefers absolute paths, but relative paths are resolved.

## Modules

### **`Logger()`**
Initializes a logger instance. Contains the log() function

*\__init__* (self, config_path=None)<br>

Initializes instances of `CompileLog()`, `HandleOutput()`<br>
Initializes the config file in `HandleConfigs().get_valid_configs()`

*log* (self, message, level, exception_traceback=None)<br>

Builds log messages with `CompileLog().build_log(message, level, exception_traceback)`<br>
Handles output with `HandleOutput().handle_log_output(message, self.configs["file_locations"]["log_file_path"])`


### **`CompileLog()`**
Joins log components to build a complete log message.

*\__init__* (self, error_map, log_components)<br>

Initializes error_map from `self.configs["error_map"]`<br>
Initializes log_components from `self.configs["log_components"]`

*build_log* (self, message, error_level, exception_traceback=None)<br>

Validates falsy error_levels. `error_level = error_level or "UNKNOWN"`<br>
If the error level passed is in error_map, returns a formatted message.<br>
If the error level passed is not in error_map, returns a message using a hardcoded format.<br>`return f"[{error_level}] {message}" + (f"\n{FormatComponents.get_traceback(exception_traceback)}" if exception_traceback else "")`

### **`FormatComponents()`**
Handles ANSI color codes, datetime.now() format, and formatted tracebacks.

*get_color* (error_map, error_level) *@staticmethod*<br>

Retrieves the relevant ANSI color code for error_level in error_map.

*get_timestamp* (log_components) *@staticmethod*<br>

Retrieves the current time using datetime.now().<br>
The timestamp is formatted using log_components["timestamp_format"].<br>The default is `"%Y-%m-%d / %Hh-%Mm-%Ss"` -> `2025-02-06 / 20h-32m-11s`

*get_traceback* (error) *@staticmethod*<br>

Retrives the traceback for an exception using traceback.format_exception().<br>
If error is None, `"No error was provided"` is returned.<br>
If error is not an instance of Exception, `"Error passed with no message"` is returned.<br>
If error does not have the attribute of `"__traceback__"`, `"\nNo traceback provided"` is returned.<br>
If a valid error is passed, the error is formatted as a traceback using `''.join(traceback.format_exception(None, error, error.__traceback__)`

### **`HandleOutput()`**
Determines where a log is printed.

*\__init__* (self, output_config)<br>

Initializes terminal_output from `output_config["terminal"]`<br>
Initializes file_output from `output_config["file"]`

*handle_log_output* (self, message, file)

If terminal_output is True, message is printed to the terminal.<br>
If file_output is True, message is written to log_file_path

*log_internal_message* (message, exception_traceback=None) *@staticmethod*<br>

Prints message with a hardcoded format `print(f"\033[1;37m[INTERNAL] {message}")`<br>
If exception_traceback is a truthy value, the error passed is printed with a hardcoded format<br>`print(f"{traceback.format_exception(None, exception_traceback, exception_traceback.__traceback__)}")`

### **`HandleConfigs()`**
Loads Logger configs. Handles validation for malformed configs, and creating a config if one doesn't exist in the specified directory.

<details>
<summary>FALLBACK_CONFIGURATION</summary>

{
    "log_components": {<br>
        "color": true,<br>
        "timestamp": true,<br>
        "timestamp_format": "%Y-%m-%d / %Hh-%Mm-%Ss",<br>
        "message": true,<br>
        "level": true<br>
    },<br><br>

    "error_map": {<br>
        "INFO": {<br>
            "color": "\\033[0;34m",<br>
            "level": "INFO",<br>
            "traceback": false<br>
        },<br>
        "DEBUG": {<br>
            "color": "\\033[0;35m",<br>
            "level": "DEBUG",<br>
            "traceback": true<br>
        },<br>
        "ERROR": {<br>
            "color": "\\033[0;31m",<br>
            "level": "ERROR",<br>
            "traceback": false<br>
        },<br>
        "WARNING": {<br>
            "color": "\\033[1;33m",<br>
            "level": "WARNING",<br>
            "traceback": true<br>
        },<br>
        "CRITICAL": {<br>
            "color": "\\033[1;35m",<br>
            "level": "CRITICAL",<br>
            "traceback": true<br>
        }<br>
    },<br><br>

    "file_locations": {<br>
        "log_file_path": "{CURRENT_PATH}"<br>
    },<br><br>

    "log_rotation_configs": {<br>
        "log_rotation": false,<br>
        "size_rotation": true,<br>
        "max_file_size": 5242880,<br>
        "time_rotation": false,<br>
        "max_file_age": 1<br>
    },<br><br>

    "output_configs": {<br>
        "terminal": true,<br>
        "file": true<br>
    }<br>
}


</details>

*\__init__* (self, config_path)<br>

If config_path is None, it is defaulted using `os.path.join(os.path.dirname(__file__), 'Logger_primary_config.JSON')`<br>
Initializes config using `get_config_map(config_path)`

*get_valid_config* (self)<br>

Helper function that runs `validate_config_types(self.configs)` and `validate_log_path()`.<br>
Returns validated config dictionary using `return self.configs`

*get_config_map* (self, config_path)<br>

Attempts to open config_path in read mode, if successful the file is read using `json.load(config_path)`<br>
If FileNotFoundError, PermissionError, or json.JSONDecodeError occur, config_path is opened in write mode, and FALLBACK_CONFIGURATION is written to config_path.
This returns FALLBACK_CONFIGURATION.

*validate_config_types* (self, configs=None)<br>

If configs is None, self.configs is assigned to configs.<br>
Iterates through key value pairs in configs, if a key is not also in FALLBACK_CONFIGURATION, the config is deemed malformed. This returns FALLBACK_CONFIGURATIONS, but does not overwrite the passed config.<br>
If a key passed has a type of dict, the key is runs through a nested loop that validates each value in the nested key.<br>
If a key does not hold the same type as the fallback key, that key is replaced with the fallback key.<br>
If a key meets all conditions, the loop is continued with no changes.

*validate_log_path* (self)<br>

Initializes path with `self.configs["file_locations"]["log_file_path"]`<br>
If path is `{CURRENT_PATH}`, path defaults to `f"{os.path.dirname(__file__)}\\log.txt"`<br>
Attempts to open path in append mode, if successful `self.configs["file_locations"]["log_file_path"]` is given the value of path.<br>
If FileNotFoundError, or PermissionError occur, file logging and log rotation are disabled.


### **`HandleRotation()`**
Manages log file rotations. Supports time and size rotation.

*\__init__* (self, configs)<br>

Initializes self.configs with configs

*check_rotation_condition* (self, full_path, max_size, max_time)<br>

If `os.path.getsize(full_path) >= max_size` or `datetime.now() - datetime.fromtimestamp(os.path.getctime(full_path)) >= timedelta(days=max_time)` are True, returns True, else returns False.

*rotate_log_path* (self)

If `self.check_rotation_condition(self.FILE_LOCATIONS["log_file_path"], self.LOG_ROTATION["max_byte_size"], self.LOG_ROTATION["max_day_length"]):` returns True, `full_rotation()` is attempted.<br>
If FileNotFoundError or PermissionError occur, an error is logged but the task isn't terminated.

*rename_rotating_log* (self, log_file_path)<br>

Initializes archive_name as `f"log_archive {datetime.now().strftime('%d_%m_%y %H_%M_%S')}_{random.randint(1000, 9999)}.txt"`<br>
Rotating file is renamed with `os.rename(log_file_path, archive_name)`

*create_fresh_log* (self, log_file_path)<br>

Opens log_file_path in write mode, but doesn't write anything. This is only does to create a new log file.

*full_rotation* (self)

Calls `rename_rotating_log(self.configs["file_locations"]["log_file_path"])` and `create_fresh_log(self.configs["file_locations"]["log_file_path"])`

## Project Tree

    Logger_primary_config.JSON    # The default configuration file.
    docs/
        index.md  # The documentation homepage.
