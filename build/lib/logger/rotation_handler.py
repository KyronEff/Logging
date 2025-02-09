import os
import shutil
import sys
from random import randint
from datetime import datetime, timedelta
from .output_handler import HandleOutput


class HandleRotation:

    def __init__(self, configs):

        self.file_path = configs["file_locations"]["log_file_path"]
        self.archive_dir = os.path.dirname(self.file_path)

        self.log_rotation = configs["log_rotation_configs"]

        self.max_size = self.log_rotation["max_file_size"] # bytes
        self.max_age = self.log_rotation["max_file_age"] # days

    def check_rotation_condition(self, full_path):

        file_size = os.path.getsize(full_path)
        file_age =  datetime.now() - datetime.fromtimestamp(os.path.getctime(full_path))

        return file_size >= self.max_size or file_age >= timedelta(days=self.max_age)

    def rotate_log_path(self):

        HandleOutput.log_internal_message("Running rotation check")

        if self.check_rotation_condition(self.file_path):

            try:

                self.full_rotation()

            except (FileNotFoundError, PermissionError) as error:

                HandleOutput.log_internal_message("An error occured whilst attempting log rotation.", exception_traceback=error)

    def rename_rotating_log(self):
        archive_name = f"log_archive_{datetime.now().strftime('%d_%m_%y %H_%M_%S')}_{randint(1000, 99999)}.txt"
        archive_path = os.path.join(self.archive_dir, archive_name)
        
        os.makedirs(self.archive_dir, exist_ok=True)

        shutil.copy2(self.file_path, archive_path)

        archive_size = (os.path.getsize(archive_path) / 1024) # size in Kilobytes
        archive_age = os.path.getmtime(archive_path) # date/time of last metadata change

        HandleOutput.log_internal_message(f"Log file Archived as {archive_name}.\nArchived file size: {archive_size:.4f} KB\nArchived file age: {archive_age}.")

    def create_fresh_log(self):

        with open(self.file_path, 'w'):
            HandleOutput.log_internal_message("Cleared log file")

    def full_rotation(self):

        self.rename_rotating_log()
        self.create_fresh_log()