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
from setproctitle import setproctitle
from meinheld import server
from docopt import docopt
from . import __version__
from oyakata.config import OyakatadConfig
from oyakata.error import ProcessError
from oyakata.process import ProcessManager, ProcessConfig

LOG_ERROR_FORMAT = r"%(asctime)s [%(process)d] [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = r"%Y-%m-%d %H:%M:%S"


class OyakataServer(object):
    def __init__(self, config):
        self.config = config
        self.pid = None
        self.manager = ProcessManager(config)
        setproctitle('oyakatad')

    def jobs(self, *args, **kwargs):
        environ = kwargs["environ"]
        method = kwargs["method"]
        sessionid = args[1][1]
        params = self._parse_params(environ['wsgi.input'].read())
        if method == "post":
            """
            register new job
            """
            print "resiger new job"
            name = params.pop("name")
            cmd = params.pop("cmd")
            config = ProcessConfig(name, cmd, **params)
            try:
                self.manager.load(config, sessionid)
                res = "OK"
                status = "200 OK"
            except ProcessError as e:
                res = e.reason
                status = str(e.errno)

        elif method == "delete":
            """
            delete jobs
            """
            print "unload job"
        elif method == "put":
            """
            update jobs
            """
            print "put"
        return status, res

    def manage(self, *args, **kwargs):
        print "manage process"

    def wsgi_app(self, environ, start_response):
        params = environ.get('PATH_INFO').split('/')[1:]
        method = environ["REQUEST_METHOD"].lower()

        if hasattr(self, str(params[0])):
            kwargs = {"method": method, "environ": environ}
            status, res = getattr(self, params[0])(*[start_response, params], **kwargs)
        else:
            status = "500"
            res = "oh"
        response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(res)))]
        start_response(status, response_headers)
        return [res]

    def _parse_params(self, param_str):
        return dict([tuple(arg.split("=")) for arg in param_str.split('&')])

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def run():
    args = docopt(__doc__, version=__version__)
    try:
        config = OyakatadConfig(args, "")
        config.load()
        s = OyakataServer(config)
        bind = config.get_bind()
        server.listen((bind[0], bind[1]))
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
