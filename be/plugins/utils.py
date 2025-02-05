import sys
import os
import logging


log = logging.getLogger(sys.argv[0])


class Env:
    def fetch(self, env_vars):
        for k in env_vars:
            dflt = None
            if isinstance(k, tuple):
                k, dflt = k
            if not (v := os.environ.get(k, dflt)):
                log.error('%s environment variable missing', k)
                sys.exit(0)
            setattr(self, k, v)


ENV = Env()


def log_setup():
    if os.environ.get('DEBUG') == 'true':
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(level=level)


def common_init(env_vars):
    log_setup()
    ENV.fetch(env_vars)
