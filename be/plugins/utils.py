import os
import logging


def log_setup():
    if os.environ.get('LOGLEVEL') == 'DEBUG':
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    logging.basicConfig(level=level)
