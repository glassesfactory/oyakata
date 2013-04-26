#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests
from requests.exceptions import ConnectionError
from .base import Command
from oyakata.process import ProcessConfig
from oyakata.procfile import Procfile


class Reload(Command):
    """
    usage: oyakata reload [-c concurrency|--concurrency concurrency]...
                        [--app APP] [<file>]

    Options:
        -h, --help
        -c concurrency,--concurrency concurrency  Specify the number processesses to run.
        --app APP
    """

    name = "reload"
    short_descr = "reload a Procfile application"

    def run(self, args, config):
        self.config = config
        procfile_path = self.config.procfile
        self._procfile_exist(procfile_path)
        self.load_procfile(procfile_path, args)

    def load_procfile(self, procfile_path, args):
        procfile = Procfile(procfile_path)
        concurrency = self.parse_concurrency(args)
        appname = self.default_appname(procfile, args)

        for name, cmd_str in procfile.processes():
            cmd, args = procfile.parse_cmd(cmd_str)
            params = dict(args=args, numprocess=concurrency.get(name, 1), cwd=os.path.abspath(procfile.root))
            try:
                url = self.config.server + '/jobs/%s' % appname
                config = ProcessConfig(name, cmd, **params).to_json()
                res = requests.put(url, config, headers={"Accept": "application/json"})
                if res.status_code != 200:
                    if res.status_code == 404:
                        print "%r is not loaded" % appname
                    else:
                        print res
                    sys.exit(1)
            except ConnectionError:
                print "oyakata server is not found..."
                sys.exit(1)
            except:
                raise
                sys.exit(1)
        print "==> %r has been reload in %s" % (appname, "http://127.0.0.1:8823")
