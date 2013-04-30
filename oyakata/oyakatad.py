#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
usage: oyakatad [--version] [-c CONFIG| --config=CONFIG] [--bind=ADDRESS]
                [--pidfile=PIDFILE] [--back_log=BACK_LOG] [--error_log=FILE]
                [--log_level=LOG_LEVEL] [--log_format=FORMAT]


Options:
    -h, --help                     show this help message and exit
    --version                      show version
    -c CONFIG, --config=CONFIG     configuration
    --pidfile=pidfile              pid file
    --back_log=BACK_LOG            default back log
    --error_log=error_log          logging error
    --log_level=LOG_LEVEL          logging level
    --log_format=FORMAT            logging format (default ltsv)

"""

import os
import pwd
import grp
import sys
import json
import logging
from setproctitle import setproctitle
from meinheld import server
from docopt import docopt
from . import __version__
from oyakata.config import OyakatadConfig
from oyakata.error import ProcessError
from oyakata.filer import JobFileManager
from oyakata.manager import ProcessManager
from oyakata.process import ProcessConfig


LOG_ERROR_FORMAT = r"%(asctime)s [%(process)d] [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = r"%Y-%m-%d %H:%M:%S"


class OyakataServer(object):
    u"""oyakata server

    :param config: server config.
    :param manager: process manager.
    :param pid: server pid file.

    """
    def __init__(self, config):
        self.config = config
        self._setup()
        self.manager = ProcessManager()
        self.filer = JobFileManager(config)
        self._load_registered_jobs()
        setproctitle('oyakatad')
        self.set_logging()

    def run(self):
        self.manager.start()
        self.manager.run()

    def jobs(self, *args, **kwargs):
        u"""manage add / remove / update jobs"""
        environ = kwargs["environ"]
        method = kwargs["method"]
        sessionid = args[1][1]
        #u-mu
        try:
            if method == "post":
                """
                register new job
                """
                config = self._get_config(environ)
                self.manager.load(config, sessionid)
                self.filer.save_job(sessionid, config)
                res = "OK"
                status = "200 OK"
            elif method == "delete":
                """
                delete jobs
                """
                name = args[1][2]
                config = self.manager.get_config(sessionid, name)
                self.manager.unload(sessionid, name)
                self.filer.delete_job(sessionid, config)
                res = "UNLOADED"
                status = "200 OK"
            elif method == "put":
                """
                reload jobs
                """
                config = self._get_config(environ)
                self.manager.reload(config, sessionid)
                self.filer.update_job(sessionid, config)
                res = "OK"
                status = "200 OK"
        except ProcessError as e:
            res = e.reason
            status = str(e.errno)
        return status, res

    def manage(self, *args, **kwargs):
        u"""manage start / stop / restart jobs"""
        sessionid = args[1][1]
        cmd = args[1][2]
        name = args[1][3]
        state = self.manager._sessions[sessionid][name]
        try:
            if cmd == "start":
                if not state.stop:
                    raise ProcessError(reason="process is already running.")
                state.stop = False
                state.reset()
                self.manager.start_job(state)
            elif cmd == "stop":
                if state.stop:
                    raise ProcessError(reason="process is already stoped.")
                self.manager.stop_job(state)
            elif cmd == "restart":
                self.manager.restart_job(state)
            res = "OK"
            status = "200 OK"
        except ProcessError as e:
            res = e.reason
            status = str(e.errno)
        except:
            raise
        return status, res

    def list(self, *args, **kwargs):
        u"""list up registered applications."""
        try:
            res = self.manager.list()
            status = "200 OK"
        except ProcessError as e:
            res = e.reason
            status = str(e.reason)
        except:
            raise
        return status, res

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

    def _get_config(self, environ):
        params = self._parse_params(environ['wsgi.input'].read())
        for key, param in params.iteritems():
            if isinstance(param, unicode):
                param = str(param)
                params[key] = param
            elif isinstance(param, list):
                new_param = []
                for p in param:
                    if isinstance(p, unicode):
                        p = str(p)
                    new_param.append(p)
                params[key] = new_param
        name = params.pop("name")
        cmd = params.pop("cmd")
        return ProcessConfig(name, cmd, **params)

    def _parse_params(self, param_str):
        return json.loads(param_str)

    def _setup(self):
        if not self.config:
            return

        if self.config.pidfile is not None:
            self._setpid()

        if self.config.user is not None:
            try:
                uid = pwd.getpwnam(self.config.user).pw_uid
            except KeyError:
                logging.error("user not found:: %s" % self.config.user)
                logging.info("failed set uid")
                raise
            os.setuid(uid)

        if self.config.group is not None:
            try:
                gid = grp.getgrnam(self.config.group).gr_gid
            except KeyError:
                raise
                logging.error("group not found:: %s" % self.config.group)
                logging.info("failed set gid")
            os.setgid(gid)

        self.jobs_file = self.config.jobs_file

    def _setpid(self):
        pid = os.getpid()
        pidfile = self.config.pidfile
        with open(pidfile, "w") as f:
            f.seek(0)
            f.write("%d" % pid)
            f.truncate()

    def _load_registered_jobs(self):
        u"""[private] load registered jobs.
        job list に登録済みのprocessを立ち上げる
        """
        self.filer.load_registered_job()
        jobs = self.filer.jobs_list["oyakata_jobs"]

        for job in jobs:
            #うーん
            sessionid = job.keys()[0]
            config_dict = job[sessionid]
            config = ProcessConfig.from_dict(config_dict)
            self.manager._load_process(config, sessionid)

    def set_logging(self, level=None):
        u"""set logging configuration.
        logging の設定をします。

        :param level:  default log level.
        """
        logger = logging.getLogger()
        if self.config.back_log is not None:
            handler = logging.FileHandler(self.config.back_log)
        else:
            handler = logging.StreamHandler()
        if self.config.log_format == "ltsv":
            format = r"""loglevel:%(levelname)s    time:[%(asctime)s]    process:[%(process)d]    body:[%(message)s]"""
        else:
            format = r"%(asctime)s [%(process)d] [%(levelname)s] %(message)s"
        datefmt = r"%Y/%m/%d:%H:%M:%S"
        handler.setFormatter(logging.Formatter(format, datefmt))
        logger.addHandler(handler)
        if not level:
            level = logging.INFO
        logger.setLevel(level)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def run():
    args = docopt(__doc__, version=__version__)
    try:
        config = OyakatadConfig(args, "")
        config.load()
    except IOError:
        print "config file is not found."
        sys.exit(1)

    try:
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
