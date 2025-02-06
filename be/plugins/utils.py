import os
import logging


def log_setup():
    if os.environ.get('DEBUG') == 'true':
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(level=level)
