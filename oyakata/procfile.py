#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import shlex

PROC_PATTERN = r'([a-zA-Z0-9_-]+):(.*)'


class Procfile(object):
    u"""Procfile object.
    Procfile オブジェクト

    :param root: application working directory.
    :param settings: parsed Procfile parameters

    """
    def __init__(self, procfile, root=None):
        self.procfile = procfile

        if not root:
            self.root = os.path.dirname(procfile) or "."
        else:
            self.root = root

        self.uid = None
        self.gid = None

        self.settings = self.parse(self.procfile)
        self._appname = None

    def processes(self):
        u"""return processes
        Procfile に記述されているプロセスを返します。
        """
        return self.settings.items()

    def parse(self, procfile_path):
        u"""parse Procfile
        Procfile をパースします。

        :param proc: target Procfile.
        """
        procfile = {}
        try:
            with open(procfile_path) as f:
                for line in f.readlines():
                    m = re.search(PROC_PATTERN, line)
                    if not m:
                        raise Exception('Bad Procfile line')
                    procfile[m.group(1)] = m.group(2)
        except IOError:
            raise
        return procfile

    def parse_cmd(self, v):
        u"""parse command. from Procfile string.
        Procfile の文字列から実行したいコマンドをパースして返します。

        :param v: parse string.
        """
        args_ = shlex.split(v)
        cmd = args_[0]
        if len(args_) > 1:
            args = args_[1:]
        else:
            args = []
        return cmd, args

    def get_appname(self):
        u"""return appname"""
        if not self._appname:
            path = os.getcwd() if self.root == "." else self.root
            self._appname = os.path.split(path)[1]
        return self._appname
