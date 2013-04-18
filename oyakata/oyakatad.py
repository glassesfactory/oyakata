#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
usage: oyakatad [--version] [-c CONFIG| --config=CONFIG] [--bind=ADDRESS]
                [--pidfile=PIDFILE] [--back_log=BACK_LOG] [--error_log=FILE]
                [--log_level=LOG_LEVEL] [--log_format=FORMAT]


Options
    -h, --help                     show this help message and exit
    --version                      show version
    -c CONFIG, --config=CONFIG     configuration
    --pidfile=PIDFILE
    --back_log=BACK_LOG            default back log
    --error_log=error_log          logging error
    --log_level=LOG_LEVEL          logging level
    --log_format=FORMAT            logging format (default ltsv)

"""

import sys
from meinheld import server
from docopt import docopt
from . import __version__
from oyakata.config import OyakatadConfig

LOG_ERROR_FORMAT = r"%(asctime)s [%(process)d] [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = r"%Y-%m-%d %H:%M:%S"


class OyakataServer(object):
    def __init__(self, config):
        self.config = config
        self.pid = None
        self.jobs = []
        self._load_jobs()

    def wsgi_app(self, environ, start_response):
        params = environ.get('PATH_INFO').split('/')[1:]
        if 'jobs' == params[0]:
            print "hoge"

        status = "200 OK"
        res = "unnbaba"
        response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(res)))]
        start_response(status, response_headers)
        return [res]

    def _load_jobs(self):
        return

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def run():
    args = docopt(__doc__, version=__version__)
    try:
        config = OyakatadConfig(args, "")
        config.load()
        s = OyakataServer(config)
        server.listen(('0.0.0.0', 8823))
        server.run(s)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        print("error: %s" % str(e))
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    run()
