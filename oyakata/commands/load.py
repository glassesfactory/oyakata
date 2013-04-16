#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from .base import Command
from oyakata.procfile import Procfile


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

    def run(self, args):
        proc = "Procfile"
        if '--procfile' in args:
            proc = args['--procfile']

        if not os.path.isfile(proc):
            if args['--procfile'] is not None:
                raise RuntimeError("procfile %r not found" % proc)
            else:
                return None
        self.load_procfile(proc, args)

    def load_procfile(self, procfile, args):
        # procfile = Procfile()
        proc = Procfile(procfile)
        appname = "unko"
        # server = 
        print proc
        concurrency = self.parse_concurrency(args)

        for name, cmd_str in proc.processes():
            print name, cmd_str
            cmd, args = proc.parse_cmd(cmd_str)
            print cmd, args
            params = dict(args=args, numprocess=concurrency.get(name, 1), cwd=os.path.abspath(proc.root))
            try:
                # server.load(params, sessionid=appname)
                print params
            except:
                print u"おんなじ名前のやつがもう動いてる☆〜（ゝ。∂）"
        print "==> %r has been loaded in %s" % (appname, "http://127.0.0.1:6969")
