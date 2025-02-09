from datetime import datetime
from output_handler import HandleOutput
import traceback


class FormatComponents:

    @staticmethod
    def get_color(error_map, error_level):

        return error_map[error_level]["color"].encode().decode("unicode_escape") 
        #.encode(),decode("unicode_escape") is used here because of 
        # how JSON files store ANSI escape sequences

    @staticmethod
    def get_timestamp(log_components):

        return f"[{datetime.now().strftime(log_components.get('timestamp_format', r'%y_%m_%d %H_%M_%S'))}]\n"

    @staticmethod
    def get_traceback(error):

        if error is None:

            HandleOutput.log_internal_message("No error was provided")
            return ""

        if not isinstance(error, Exception):
            if callable(error):

                error = error("Error passed with no message")
            else:
                HandleOutput.log_internal_message(
                    "Invalid error type or message")
                return ""

        if not hasattr(error, '__traceback__'):

            return "\nNo traceback provided"

        return "\n\033[0m" + ''.join(traceback.format_exception(None, error, error.__traceback__))
