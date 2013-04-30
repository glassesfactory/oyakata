#!/usr/bin/env python
# -*- coding: utf-8 -*-

from oyakata.config import OyakatadConfig


def test_server_config():
    config = OyakatadConfig()
    assert config is not None
