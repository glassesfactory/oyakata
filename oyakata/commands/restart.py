#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests
from requests.exceptions import ConnectionError
from .base import Command
from oyakata.procfile import Procfile


class Restart(Command):
    """
    usage: oyakata restart [--app APP] [<file>]

    Options:
        -h, --help
        --app APP
    """

    name = "restart"
    short_descr = "restart process from Procfile"

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
                url = self.config.server + '/manage/%s/restart/%s' % (appname, name)
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
        print "==> %r has been restart in %s" % (appname, "http://127.0.0.1:8823")
