#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyuv
from oyakata.process import ProcessConfig
from oyakata.state import ProcessState, ProcessWatcher

#for test.
config = ProcessConfig()
sessionid = "test_dummy"


def test_state_simple():
    state = ProcessState(config, sessionid)
    assert state


def test_state_update():
    state = ProcessState(config, sessionid)

    new_config = ProcessConfig()
    state.udpate(config)
    assert "update ?"


def test_state_reset():
    state = ProcessState(config, sessionid)

    assert "reset ?"


def test_state_queuing():
    state = ProcessState(config, sessionid)
    assert state


def test_state_list_process():
    state = ProcessState(config, sessionid)
    assert state


#--------- watcher ---------

loop = pyuv.Loop.default.loop()


def test_watcher_simple():
    watcher = ProcessWatcher(loop)
    assert "simple"


def test_watcher_start_stop():
    watcher = ProcessState(loop)


def test_watcher_close():
    watcher = ProcessState(loop)


def test_watcher_check():
    watcher = ProcessState(loop)
    assert "hgoeee"
