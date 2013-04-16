#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import Command


class Bals(Command):
    """
    usage: oyakata bals
    """
    name = "bals"
    short_descr = "I'm gonna wait for 3 minutes!!"

    def run(self, args):
        return
