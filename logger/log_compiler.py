from format_util_ import FormatComponents

class CompileLog:

    def __init__(self, error_map, log_components):

        self.error_map = error_map
        self.color = log_components["color"]
        self.timestamp = log_components["timestamp"]
        self.level = log_components["level"]
        self.message = log_components["message"]

    def build_log(self, message, error_level="DEFAULT", exception_traceback=None):
            
            error_level_info = self.error_map.get(error_level, self.error_map["DEFAULT"])

            final_log = [
                FormatComponents.get_color(
                    self.error_map, error_level_info) if self.color else "",
                FormatComponents.get_timestamp(
                    self.log_components) if self.timestamp else "",
                f"[{error_level}] " if self.level else "",
                f"{message}" if self.message else "",
                FormatComponents.get_traceback(
                    exception_traceback) if error_level_info["traceback"] and exception_traceback else ""
            ]

            return ''.join(final_log)