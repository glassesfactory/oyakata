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
        proc = "Procfile"
        if '--procfile' in args:
            proc = args['--procfile']

        if not os.path.isfile(proc):
            if args['--procfile'] is not None:
                raise RuntimeError("procfile %r not found" % proc)
            else:
                return None
        self.config = config
        self.load_procfile(proc, args)

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
