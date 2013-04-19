#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
from .base import Command
from oyakata.procfile import Procfile
from oyakata.process import ProcessConfig


class Load(Command):
    """
    usage: oyakata load [-c concurrency|--concurrency concurrency]...
                        [--app APP] [<file>]

    -h, --help
    -c concurrency,--concurrency concurrency  Specify the number processesses
                                              to run.
    --app APP
    """

    name = "load"
    short_descr = "load a Procfile application"

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
        # procfile = Procfile()
        proc = Procfile(procfile)
        concurrency = self.parse_concurrency(args)
        appname = "unko"

        for name, cmd_str in proc.processes():
            print name, cmd_str
            cmd, args = proc.parse_cmd(cmd_str)
            print cmd, args
            params = dict(args=args, numprocess=concurrency.get(name, 1), cwd=os.path.abspath(proc.root))
            try:
                url = self.config.server + '/jobs/%s' % appname
                config = ProcessConfig(name, cmd, **params).to_dict()
                print config
                res = requests.post(url, config)
                print res
            except:
                raise
                # print u"おんなじ名前のやつがもう動いてる☆〜（ゝ。∂）"
        print "==> %r has been loaded in %s" % (appname, "http://127.0.0.1:8823")
