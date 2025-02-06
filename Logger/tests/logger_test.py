import pytest
import sys
from datetime import datetime

sys.path.append(r'D:\GitHub\Repos\Logging\custom_logging_library')

from logging_lib.logger import Logger

@pytest.fixture
def logger():
    return Logger()

@pytest.mark.parametrize('message, level, exception, expected_output',
    [
        ("Info log", "INFO", None, ("[INFO] Info log", datetime.now().strftime("%Y-%m-%d / %Hh-%Mm-%Ss"))),
        ("Debug log", "DEBUG", None, ("[DEBUG] Debug log", datetime.now().strftime("%Y-%m-%d / %Hh-%Mm-%Ss"))),
        ("Error log", "ERROR", None, ("[ERROR] Error log", datetime.now().strftime("%Y-%m-%d / %Hh-%Mm-%Ss"))),
        ("Warning log", "WARNING", None, ("[WARNING] Warning log", datetime.now().strftime("%Y-%m-%d / %Hh-%Mm-%Ss"))),
        ("Critical log", "CRITICAL", None, ("[CRITICAL] Critical log", datetime.now().strftime("%Y-%m-%d / %Hh-%Mm-%Ss"))),
        (123, "TEST", None, ("[TEST] 123"),),
        (0.01, "TEST", None, ("[TEST] 0.01",)),
        ("Test", "TEST", TypeError, ("[TEST] Test", "TypeError: No other information provided")),
        ("Test", "TEST", TypeError("Test exception"), ("[TEST] Test", "TypeError: Test exception")),
        ("", "TEST", None , ("[TEST]",)),
        (("a" * 256), "TEST", None , ("[TEST]", "a" * 256,)),
        ("Test", None, None, ("[UNKNOWN] Test",)),
        ("Test\nNewline", "TEST", None, ("[TEST] Test\nNewline",))
    ]
    )

def test_log(logger, capsys, message, level, exception, expected_output):

    logger.log(message, level, exception)
    
    termoutput = capsys.readouterr()

    for output in expected_output:
        assert output in termoutput.out

