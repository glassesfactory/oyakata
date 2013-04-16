#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import shlex

PROC_PATTERN = r'([a-zA-Z0-9_-]+):(.*)'


class Procfile(object):
    def __init__(self, procfile, root=None):
        self.procfile = procfile

        if not root:
            self.root = os.path.dirname(procfile) or "."
        else:
            self.root = root

        self.uid = None
        self.gid = None

        self.settings = self.parse(self.procfile)

    def processes(self):
        return self.settings.items()

    def parse(self, proc):
        procfile = {}
        with open(proc) as f:
            for line in f.readlines():
                m = re.search(PROC_PATTERN, line)
                if not m:
                    raise Exception('Bad Procfile line')
                procfile[m.group(1)] = m.group(2)
        return procfile

    def parse_cmd(self, v):
        args_ = shlex.split(v)
        print args_
        cmd = args_[0]
        if len(args_) > 1:
            args = args_[1]
        else:
            args = []
        return cmd, args
