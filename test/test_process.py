#!/usr/bin/env python
# -*- coding: utf-8 -*-

from oyakata.process import ProcessConfig


#dummy cmd...
DUMMY_CMD = {
    "name": "test_cmd",
    "cmd": "ls",
    "args": "-l",
    "cwd": "test/testapp"
}


def test_simple():
    config = ProcessConfig()
    print config
    assert "hogeee"


def test_from_dict():
    assert "uhgaaa"


def test_to_dict():
    assert "dictttt"


def test_to_json():
    assert "jsonooooonn"


def test_make_process():
    assert "processssssss"
