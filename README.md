# Logger

A lightweight logging library for Python with features like log rotation and configurable error levels.

## Installation
You can install the package using pip:

```bash
pip install logger

## Basic usage

from logger import Logger

logger = Logger() # Accepts a JSON config file. Uses internal validation

logger.log("This is a log message", "INFO")
