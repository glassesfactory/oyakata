#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from oyakata.config import OyakatadConfig
from oyakata.filer import JobFileManager


def test_load_file():
    #うーん
    config = OyakatadConfig()
    config.load()

    filer = JobFileManager(config)
    jobs = filer.load_registered_jobs()["oyakatad"]


def test_save_job():
    assert "jobs"


def test_delete_job():
    assert "jobs"


def test_update_job():
    assert "update"
