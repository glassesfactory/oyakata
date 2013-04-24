#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests
from requests.exceptions import ConnectionError
from oyakata.procfile import Procfile
from .base import Command


class Stop(Command):
    """
    usage: oyakata stop [--app APP] [<file>]

    Options:
        -h, --help
        --app APP
    """

    name = "stop"
    short_descr = "stop process from Procfile"

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
                url = self.config.server + '/manage/%s/stop/%s' % (appname, name)
                res = requests.get(url)
                if res.status_code != 200:
                    if res.status_code == 404:
                        print "%r is not loaded." % appname
                    else:
                        print res
                    sys.exit(1)
            except ConnectionError:
                print "oyakata server is not found..."
                sys.exit(1)
            except:
                raise
                sys.exit(1)
        print "==> %r has been stoped in %s" % (appname, "http://127.0.0.1:8823")
