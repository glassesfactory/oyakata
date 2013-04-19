#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
from .base import Command


class List(Command):
    """
    usage: oyakata list

    -h, --help
    """
    name = "list"
    short_descr = "job list"

    def run(self, args, config):
        try:
            res = requests.get('')
        except:
            print "ouhu..."
            sys.exit(1)
