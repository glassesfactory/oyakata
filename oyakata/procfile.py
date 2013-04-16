#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

PROC_PATTERN = r'([a-zA-Z0-9_-]+):(.*)'


class Procfile(object):
    def __init__(self, procfile):
        self.procfile = procfile

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
