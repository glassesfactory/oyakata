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
        self.config = config
        procfile_path = self.config.procfile
        self._procfile_exist(procfile_path)
        self.load_procfile(procfile_path, args)

    def load_procfile(self, procfile_path, args):
        procfile = Procfile(procfile_path)
        appname = self.default_appname(procfile, args)

        for name, cmd_str in procfile.processes():
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
