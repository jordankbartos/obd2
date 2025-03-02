import logging
import logging.handlers
import queue
import sys
import threading
from pathlib import Path

from config import LOG_FILE, LOG_FMT, LOG_LEVEL

_log_file = Path(LOG_FILE)
if not _log_file.exists():
    _log_file.parent.mkdir(parents=True, exist_ok=True)

_log_queue = queue.Queue()

_formatter = logging.Formatter(LOG_FMT)


def _log_listener(queue):
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(_formatter)

    stream_handler = logging.StreamHandler(stream=sys.stderr)
    stream_handler.setLevel(LOG_LEVEL)
    stream_handler.setFormatter(_formatter)

    while True:
        record = queue.get()
        if record is None:
            break
        file_handler.emit(record)
        stream_handler.emit(record)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # add queue handler for multi-threaded logging
    queue_handler = logging.handlers.QueueHandler(_log_queue)
    logger.addHandler(queue_handler)
    return logger


_log_thread = threading.Thread(target=_log_listener, args=(_log_queue,))
_log_thread.daemon = True
_log_thread.start()
