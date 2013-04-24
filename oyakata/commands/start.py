#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests
from requests.exceptions import ConnectionError
from .base import Command
from oyakata.procfile import Procfile


class Start(Command):
    """
    usage: oyakata start [--app APP] [<file>]

    Options:
        -h, --help
        --app APP
    """

    name = "start"
    short_descr = "start a process from Procfile"

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
        appname = self.default_appname(proc, args)

        for name, cmd_str in proc.processes():
            try:
                url = self.config.server + '/manage/%s/start/%s' % (appname, name)
                res = requests.get(url)
                if res.status_code != 200:
                    if res.status_code == 404:
                        print "%r is not loaded." % appname
                    elif res.status_code == 400:
                        print "%r is already running." % appname
                    else:
                        print res
                    sys.exit(1)
            except ConnectionError:
                print "oyakata server is not found..."
                sys.exit(1)
            except:
                raise
                sys.exit(1)
        print "==> %r has been started in %s" % (appname, "http://127.0.0.1:8823")
