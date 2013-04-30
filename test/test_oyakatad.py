#!/usr/bin/env python
# -*- coding: utf-8 -*-

from oyakata.config import OyakatadConfig
from oyakata.oyakatad import OyakataServer

dummy_args = []
config = OyakatadConfig(dummy_args, "")
config.load()


def test_simple():
    d = OyakataServer(config)
    pass
