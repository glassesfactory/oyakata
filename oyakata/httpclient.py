#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests


class Client(object):
    def __init__(self, url):
        self.url = url
        return

    def load(self, configs, args):
        try:
            res = requests.post('http://127.0.0.1:8823/jobs', {'hironori': 'boorin'})
            print res
        except Exception as e:
            print e
        return res
