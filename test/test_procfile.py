#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from oyakata.procfile import Procfile

procfile_path = 'Procfile'
#dummy: python dummy.py unko
error_proc = 'ErrorProcfile'
dummy_path = 'ugo'


def test_procfile():
    procfile = Procfile(procfile_path)
    assert procfile is not None
    assert len(procfile.settings) > 0
    #test unexist Procfile.
    with pytest.raises(IOError):
        procfile = Procfile(dummy_path)
    #test syntax error

    with pytest.raises(Exception):
        procfile = Procfile(error_proc)


def test_procfile_processes():
    procfile = Procfile(procfile_path)
    assert len(procfile.processes()) > 0 < 2


def test_procfile_parse_cmd():
    procfile = Procfile(procfile_path)
    for name, cmd_str in procfile.processes():
        cmd, args = procfile.parse_cmd(cmd_str)
        assert cmd == 'python'
        assert len(args) == 2


def test_procfile_get_appname():
    procfile = Procfile(procfile_path)
    appname = procfile.get_appname()
    assert appname is not None
    assert appname == 'oyakata'
