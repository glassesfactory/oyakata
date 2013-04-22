#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib
from collections import OrderedDict
import logging, subprocess, select

from .error import ProcessConflict


def _create_logger(name, level=None):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    #LTVS ふぉーまっとにすっか
    logger.addHandler(handler)
    if not level:
        level = logging.INFO
    logger.setLevel(level)
    return logger


class ProcessManager(object):
    """
    manage process.
    """
    def __init__(self, config):
        self.config = config
        self._sessions = OrderedDict()
        self.processes = OrderedDict()
        self.running_process = OrderedDict()
        self.loggers = {}
        self.loggers['system'] = _create_logger('system')

        self._load_registerd_jobs()

    def load(self, config, sessionid):
        print "in processmanager::", config, sessionid
        print "----------------\n"

        if sessionid in self._sessions:
            raise ProcessConflict()
        cmd = config.cmd
        name = config.name
        config_args = config.settings
        cmd_args = config_args.get("args", None)
        exc_cmd = [cmd, cmd_args]
        cwd = urllib.unquote(config_args.get("cwd"))
        p = subprocess.Popen(exc_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, cwd=cwd)
        self._sessions[sessionid] = {}
        self._sessions[sessionid][name] = p
        print p.pid
        self.loggers[p.pid] = logger = _create_logger('%s.%d' % (name, 1 + 1))
        logger.info('started with pid')

        jobs_path = self.config.jobs_file
        self._save_job(sessionid, config)
        # jobs_json = json.loads(f.rea
        # print jobs_json
        # p = subprocess.Popen()
        return

    def _load_registerd_jobs(self):
        jobs_path = self.config.jobs_file
        if not os.path.isfile(jobs_path):
            return
        with open(jobs_path) as f:
            data = f.read()
            if data == '':
                self._init_jobs_file()
                return
            else:
                self.jobs_list = json.loads(data)

        jobs = self.jobs_list["oyakata_jobs"]
        for job in jobs:
            sessionid = job.keys()[0]
            config = job[sessionid]
            print config
        return

    def _init_jobs_file(self):
        jobs_path = self.config.jobs_file
        with open(jobs_path, "r+") as f:
            jobs_list = json.dumps({"oyakata_jobs": []})
            f.write(jobs_list)
        self.jobs_list = jobs_list

    def _save_job(self, sessionid, config):
        job = {}
        job[sessionid] = config.to_dict()
        self.jobs_list["oyakata_jobs"].append(job)
        jobs_path = self.config.jobs_file
        with open(jobs_path, "w") as f:
            try:
                f.seek(0)
                f.write(json.dumps(self.jobs_list))
                f.truncate()
            except IOError:
                print "oh"

    def start_all(self):
        for id, cmd in self.proc:
            for i in xrange(int(self.concurrencies.get(id, 1))):
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=self.env, cwd=self.cwd)
                self.processes.append(p)
                self.loggers[p.pid] = logger = _create_logger('%s.%d' % (id, i + 1))
                logger.info('started with pid')

    def stop_all(self):
        return

    def watch(self):
        # for p in self.processes:
        try:
            self.running = True
            while self.running:
                pass
        except select.error:
            pass
        finally:
            logger = self.loggers['system']
            logger.info('sending SIGTERM to all processs')
            for p in self.processs:
                p.terminate()

    def interrupt(self):
        self.running = False


class Process(object):
    """
    process wrapper
    """

    def __init__(self, cmd, args=None, env=None, uid=None, gid=None, shell=False):
        self.cmd = cmd

    def spawn(self):
        """
        start processs
        """
        return

import json


class ProcessConfig(object):
    def __init__(self, name, cmd, **settings):
        self.name = name
        self.cmd = cmd
        self.settings = settings

    def to_dict(self):
        d = dict(name=self.name, cmd=self.cmd)
        d.update(self.settings)
        return d

    def to_json(self):
        return json.dumps(self.to_dict())
