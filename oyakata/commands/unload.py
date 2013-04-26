#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
from requests.exceptions import ConnectionError
from .base import Command
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
        self.config = config
        procfile_path = self.config.procfile
        self._procfile_exist(procfile_path)
        self.load_procfile(procfile_path, args)

    def load_procfile(self, procfile_path, args):
        procfile = Procfile(procfile_path)
        appname = self.default_appname(procfile, args)

        for name, cmd_str in procfile.processes():
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
