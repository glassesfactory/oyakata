#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import Command


class Unload(Command):
    """
    usage: oyakata unload
    """
    name = 'unload'
    short_descr = "unload a Procfile application"

    def run(self, args):
        return
