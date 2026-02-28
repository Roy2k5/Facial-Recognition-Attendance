import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

from core import settings


class Logger:
    def __init__(self, name="", log_level=logging.INFO, log_file=None):
        self.log = logging.getLogger(name)
        self.get_logger(log_level, log_file)

    def get_logger(self, log_level, log_file):
        self.log.setLevel(log_level)
        self._init_formatter()
        if log_file is not None:
            self._add_file_handler(os.path.join(settings.log_dir, log_file))
        else:
            self._add_stream_handler()

    def _init_formatter(self):
        self.formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    def _add_stream_handler(self):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(self.formatter)
        self.log.addHandler(stream_handler)

    def _add_file_handler(self, log_file):
        file_handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=10)
        file_handler.setFormatter(self.formatter)
        self.log.addHandler(file_handler)

    def info(self, msg):
        self.log.info(msg)

    def warning(self, msg):
        self.log.warning(msg)

    def error(self, msg):
        self.log.error(msg)


if not os.path.exists(settings.log_dir):
    os.makedirs(settings.log_dir, exist_ok=True)
app_logger = Logger("BACKEND", log_file="http.log")
