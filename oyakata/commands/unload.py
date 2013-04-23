#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests
from requests.exceptions import ConnectionError
from .base import Command
from oyakata.error import ProcessNotFound
from oyakata.process import ProcessConfig
from oyakata.procfile import Procfile


class Unload(Command):
    """
    usage: oyakata unload [--app APP] [<file>]

    Options:
        -h, --help
        --app APP
    """
    name = 'unload'
    short_descr = "unload a Procfile application"

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
            url = self.config.server + '/jobs/%s/%s' % (appname, name)
            try:
                res = requests.delete(url)
                if res.status_code != 200:
                    if res.status_code == 404:
                        print "%r has not loaded" % appname
                    sys.exit(1)
            except ConnectionError:
                print "oyakata server is not found..."
                sys.exit(1)
            except:
                raise
                sys.exit(1)

        print "==> %r has been unloaded in %s" % (appname, "http://127.0.0.1:8823")
