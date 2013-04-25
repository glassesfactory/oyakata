#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
from requests.exceptions import ConnectionError
from .base import Command


class List(Command):
    """
    usage: oyakata list

    -h, --help
    """
    name = "list"
    short_descr = "job list"

    def run(self, args, config):
        url = config.server + '/list'
        try:
            res = requests.get(url)
            if res.status_code != 200:
                print "%s server error..." % res.status_code
                sys.exit(1)
            print "registerd application list"
            print "--------------------------------"
            print "app name | status | processes"
            print "--------------------------------"
            print res.text
        except ConnectionError:
            print "oyakata server is not found..."
            sys.exit(1)
        except:
            raise
            sys.exit(1)
