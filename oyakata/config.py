#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tomlpython as toml


class CliConfig(object):
    """
    oyakata config obj
    """
    def __init__(self, args):
        self.server = args['--url'] or 'http://127.0.0.1:8823'
        if '--root'in args:
            self.root = args['--url']
        else:
            self.root = os.getcwd()

        self.procfile = args['--procfile'] or 'Procfile'


class OyakatadConfig(object):
    """
    oyakatad config obj

    :param args: lounch command line args.
    :param cfg: config object.

    """

    def __init__(self, args, config_dir):
        self.args = args
        self.config_dir = config_dir
        self.cfg = None

        self._set_defaults()

    def load(self):
        """
        read config file and set params.
        """
        config_path = os.path.join(self.config_dir, "oyakata.toml")
        if os.path.isfile(config_path):
            self.parse_config(config_path)

        self.bind = self.args['--bind'] or self.bind

        if self.args['--pidfile'] is not None:
            self.pidfile = self.args['--pidfile']

        if self.args['--error_log'] is not None:
            self.error_log = self.args['--error_log']

        if self.args['--log_level'] is not None:
            self.error_log = self.args['--log_level']

        if self.args['--log_format'] is not None:
            self.log_format = self.args['--log_format']

    def parse_config(self, config_path):
        """
        parse config file.

        :param config_path: config file path.

        """
        with open(config_path) as f:
            config = toml.parse(f)
        self.cfg = config

        oyakata_cfg = self.cfg.get("oyakatad", None)
        if oyakata_cfg:
            self.bind = oyakata_cfg.get("bind", "0.0.0.0:8823")
            self.pidfile = oyakata_cfg.get("pidfile", None)
            self.back_log = oyakata_cfg.get("back_log", None)
            self.error_log = oyakata_cfg.get("error_log", None)
            self.log_level = oyakata_cfg.get("log_level", "info")
            self.log_format = oyakata_cfg.get("log_format", "ltsv")
            self.user = oyakata_cfg.get("user", None)
            self.group = oyakata_cfg.get("group", None)
            self.jobs_file = oyakata_cfg.get("jobs_file", "oyakata_jobs.dat")

    def get_bind(self):
        address = self.bind.split(':')
        return (address[0], int(address[1]))

    #u-n
    def _set_defaults(self):
        self.bind = "0.0.0.0:8823"
        self.pidfile = None
        #nnn-
        self.back_log = None
        self.error_log = None
        self.log_level = "info"
        self.log_format = "ltsv"

        self.uid = None
        self.gid = None

    def to_dict(self):
        pass

    def to_json(self):
        pass
