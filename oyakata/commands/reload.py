#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import Command


class Reload(Command):
    """
    usage: oyakata reload
    """

    name = "reload"
    short_descr = "reload a Procfile application"

    def run(self, args, config):
        return
