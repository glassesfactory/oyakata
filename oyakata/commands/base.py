#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict
import os
import sys
import copy


KNOWN_COMMANDS = []


def get_commands():
    commands = OrderedDict()
    for c in KNOWN_COMMANDS:
        cmd = c()
        commands[c.name] = cmd.copy()
    return commands


class CommandMeta(type):
    def __new__(cls, name, bases, attrs):
        super_new = type.__new__
        parents = [cmd for cmd in bases if isinstance(cmd, CommandMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        attrs["order"] = len(KNOWN_COMMANDS)
        new_cls = super_new(cls, name, bases, attrs)
        KNOWN_COMMANDS.append(new_cls)
        return new_cls


class Command(object):
    u"""
    oyakata Command Base Class
    """
    def run(self, args, config):
        raise NotImplementedError

    def copy(self):
        return copy.copy(self)

    def default_appname(self, procfile, args):
        if args['--app']:
            appname = args['--app']
            if appname == ".":
                appname = procfile.get_appname()
        elif procfile is not None:
            appname = procfile.get_appname()
        else:
            appname = "default"
        return appname

    def parse_concurrency(self, args):
        if not '--concurrency' in args:
            return {}
        settings = {}
        for setting in args['--concurrency']:
            kv = setting.split('=')
            if len(kv) == 2:
                key = kv[0].strip()
                try:
                    v = int(kv[1].strip())
                except ValueError:
                    continue
                settings[key] = v
        return settings

Command = CommandMeta('Command', (Command,), {})