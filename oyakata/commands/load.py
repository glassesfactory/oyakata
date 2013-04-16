#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from .base import Command
from oyakata.procfile import Procfile


class Load(Command):
    """
    usage: oyakata load
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
        self.load_procfile(proc)

    def load_procfile(self, procfile):
        # procfile = Procfile()
        print procfile
        proc = Procfile(procfile)
        print proc
        # with open() as f:
            # for line in f.readlines():
                # match = re.search(r'([a-zA-Z0-9_-]+):(.*)', line)
                # if not match:
                    # raise Exception('Bad Procfile line.')
                # procfile[match.group(1)] = match.group(2)
        print procfile
