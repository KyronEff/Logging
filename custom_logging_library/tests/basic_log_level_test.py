import pytest
import sys
import os

# Add the root project folder to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from custom_logging_library.logging_lib.logger import Logger  # type: ignore # Correct import

@pytest.fixture
def logger():
    return Logger()

@pytest.mark.parametrize("message, expected", [
    ("Info log test", "[INFO] Info log test")
])
def test_info_log(logger, message, expected, capsys):
    logger.info_log(message)

    cap_result = capsys.readouterr()

    assert expected in cap_result.out

def test_debug_log(logger, capsys):
    logger.debug_log("Debug log test")

    cap_result = capsys.readouterr()

    assert '[DEBUG]' in cap_result.out
    assert 'Debug log test' in cap_result.out

def test_error_log(logger, capsys):
    logger.error_log("Error log test")

    cap_result = capsys.readouterr()

    assert '[ERROR]' in cap_result.out
    assert 'Error log test' in cap_result.out

def test_warning_log(logger, capsys):
    logger.warning_log("Warning log test")

    cap_result = capsys.readouterr()

    assert "[WARNING]" in cap_result.out
    assert 'Warning log test' in cap_result.out

def test_critical_log(logger, capsys):
    logger.critical_log("Critical log test")

    cap_result = capsys.readouterr()

    assert "[CRITICAL]" in cap_result.out
    assert 'Critical log test' in cap_result.out

os.system("pytest tests/basic_log_level_tests.py")
