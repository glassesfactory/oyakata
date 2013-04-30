#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib
import logging
import subprocess
from collections import OrderedDict
from threading import RLock

import pyuv

import json


class ProcessConfig(object):
    u"""Process config object.
    プロセスの設定オブジェクト

    Attributes:
    :param name: process name.
    :param cmd: exec command.
    :param settings: process settings.

    """

    DEFAULT_PARAMS = {
        "args": [],
        "env": {},
        "uid": None,
        "gid": None,
        "cwd": None,
        "shell": False,
        "preexec_fn": None
        # "redirect_output": [],
        # "redirect_input": False,
    }

    def __init__(self, name, cmd, **settings):
        self.name = name
        self.cmd = cmd
        self.settings = settings

    @classmethod
    def from_dict(cls, config):
        u"""create ProcessConfig instance from dict object.
        dict から ProcessConfig インスタンスを生成します。

        :param config: config dict

        """
        d = config.copy()
        try:
            name = d.pop('name')
            cmd = d.pop('cmd')
        except KeyError:
            raise ValueError('invalid dict....')
        return cls(name, cmd, **d)

    def to_dict(self):
        u"""convert to dict.
        dict に変換します。

        """
        d = dict(name=self.name, cmd=self.cmd)
        d.update(self.settings)
        return d

    def to_json(self):
        u"""convert to json.
        json に変換します。
        """
        return json.dumps(self.to_dict())

    def _update_default_param(self):
        params = {}
        for k, v in self.DEFAULT_PARAMS.iteritems():
            params[k] = self.settings.get(k, v)

        self.env = params.get("env", None)

        return params

    def make_process(self):
        cmd = self.cmd
        params = self._update_default_param()
        cmd_args = params.get("args", None)
        if not isinstance(cmd_args, list):
            cmd_args = [cmd_args]
        exc_cmd = [cmd]
        exc_cmd.extend(cmd_args)
        cwd = urllib.unquote(params.get("cwd"))

        shell = params.get('shell', False)
        return subprocess.Popen(exc_cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=shell, cwd=cwd, env=None)


# class Process(object):
#     def __init__(self, loop, cmd, args=[], uid=None, gid=None,
#                  env=None, cwd=None):
#         pass

#     def spawn(self):
#         pass

#     def stop(self):
#         pass

#     @property
#     def active(self):
#         return
