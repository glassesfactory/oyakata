#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests
from requests.exceptions import ConnectionError
from .base import Command
from oyakata.procfile import Procfile
from oyakata.process import ProcessConfig


class Load(Command):
    """
    usage: oyakata load [-c concurrency|--concurrency concurrency]...
                        [--app APP] [<file>]

    Options:
        -h, --help
        -c concurrency,--concurrency concurrency  Specify the number processesses to run.
        --app APP                                 Application
    """

    name = "load"
    short_descr = "load a Procfile application"

    def run(self, args, config):
        self.config = config
        procfile = self.config.procfile
        self._procfile_exist(procfile)
        self.load_procfile(procfile, args)

    def load_procfile(self, procfile, args):
        proc = Procfile(procfile)
        concurrency = self.parse_concurrency(args)
        appname = self.default_appname(proc, args)

        for name, cmd_str in proc.processes():
            cmd, args = proc.parse_cmd(cmd_str)
            params = dict(args=args, numprocess=concurrency.get(name, 1), cwd=os.path.abspath(proc.root))
            try:
                url = self.config.server + '/jobs/%s' % appname
                config = ProcessConfig(name, cmd, **params).to_json()
                res = requests.post(url, config, headers={"Accept": "application/json"})
                if res.status_code != 200:
                    if res.status_code == 409:
                        print "%r is already loaded." % appname
                    else:
                        print res
                    sys.exit(1)
            except ConnectionError:
                print "oyakata server is not found..."
                sys.exit(1)
            except:
                raise
                sys.exit(1)
        print "==> %r has been loaded in %s" % (appname, "http://127.0.0.1:8823")
