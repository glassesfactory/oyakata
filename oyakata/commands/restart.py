#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import Command


class Restart(Command):
    """
    usage: oyakata restart
    """

    name = "restart"
    short_descr = "restart process from Procfile"

    def run(self, args, config):
        return
