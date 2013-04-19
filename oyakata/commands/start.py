#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import Command


class Start(Command):
    """
    usage: oyakata start
    """

    name = "start"
    short_descr = "start a process from Procfile"

    def run(self, args, config):
        return
