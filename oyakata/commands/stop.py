#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import Command


class Stop(Command):
    """
    usage: oyakata stop
    """

    name = "stop"
    short_descr = "stop process from Procfile"

    def run(self, args, config):
        return
