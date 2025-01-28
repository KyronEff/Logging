@echo off
REM Batch script to create the custom_logging_library folder structure

REM Root folder
mkdir custom_logging_library
cd custom_logging_library

REM Main library folder and files
mkdir logging_lib
cd logging_lib
echo. > __init__.py
echo. > logger.py
echo. > formatters.py
echo. > handlers.py
echo. > levels.py
echo. > config.py
cd ..

REM Examples folder and files
mkdir examples
cd examples
echo. > basic_example.py
echo. > advanced_example.py
cd ..

REM Tests folder and files
mkdir tests
cd tests
echo. > __init__.py
echo. > test_logger.py
echo. > test_formatters.py
echo. > test_handlers.py
cd ..

REM Documentation folder and files
mkdir docs
cd docs
echo. > overview.md
echo. > setup.md
echo. > api_reference.md
cd ..

REM Optional files
echo. > LICENSE
echo. > README.md
echo. > requirements.txt
echo. > setup.py
echo. > pyproject.toml

echo Folder structure created successfully!
