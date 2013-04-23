#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib
import logging
import subprocess
import select
from collections import OrderedDict, deque
from threading import RLock

from .error import ProcessError, ProcessConflict, ProcessNotFound


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
        self._lock = RLock()

        self._load_registerd_jobs()

    def load(self, config, sessionid):
        print "load and save process to config file."
        print "in processmanager::", config, sessionid
        print "----------------\n"

        try:
            self._load_process(config, sessionid)
        except ProcessError:
            raise

        self._save_job(sessionid, config)
        return

    def unload(self, sessionid, name):
        print "unload and delete process from config file."
        if not sessionid in self._sessions:
            raise ProcessNotFound()
        else:
            print "uwaaaaa"

        print self._sessions[sessionid]
        state = self._sessions[sessionid][name]
        config = state.config
        try:
            self._unload_process(state, config, sessionid)
            print "oppai"
        except ProcessError:
            raise
        # self._delete_job(sessionid, config)

    def _load_process(self, config, sessionid):
        if sessionid in self._sessions:
            raise ProcessConflict()
        else:
            self._sessions[sessionid] = OrderedDict()

        with self._lock:
            state = ProcessState(config, sessionid)
            self._sessions[sessionid][config.name] = state

        self.start_job(state)
        # self.loggers[p.pid] = logger = _create_logger('%s.%d' % (name, 1 + 1))
        # logger.info('started with pid')

    def _unload_process(self, state, config, sessionid):
        u"""process の unload"""
        try:
            self.stop_job(state)
        except:
            raise
        u"""del のほうがいいのかな"""
        # self._sessions[sessionid].pop(config.name)
        # try:
            # del self._sessions[sessionid]
        # except KeyError:
            # pass
        # self._sessions.pop(sessionid)

    def start_job(self, state):
        u"""job を開始する"""
        if state.stop:
            return

        if len(state.running) < state.numprocess:
            self._spawn_processes(state)

    def stop_job(self, state):
        u"""job を停止する"""
        with self._lock:
            state.numprocess = 0
            state.stop = True
            while True:
                group = state.running
                try:
                    p = group.popleft()
                except IndexError:
                    break

                self.running_process.pop(p.pid)
                #logging kill process
                #logger["p.pid"].info("stop_process %s:%s" %(p.name, p.pid))
                p.kill()

    def _spawn_processes(self, state):
        u"""指定された数で process を立ち上げる"""
        num_to_start = state.numprocess - len(state.running)
        for i in range(num_to_start):
            self._spawn_process(state)

    def _spawn_process(self, state):
        u"""process を立ち上げる"""
        p = state.make_process()
        state.queue(p)
        pid = p.pid
        self.running_process[pid] = p
        self.loggers[pid] = logger = _create_logger('%s.%d' % (state.config.name, 1 + 1))
        logger.info('started with pid')

    def _load_registerd_jobs(self):
        u"""job list に登録済みのprocessを立ち上げる"""
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
            config_dict = job[sessionid]
            config = ProcessConfig.from_dict(config_dict)
            self._load_process(config, sessionid)
        return

    def _init_jobs_file(self):
        u"""job file を作成する"""
        jobs_path = self.config.jobs_file
        with open(jobs_path, "r+") as f:
            jobs_list = {"oyakata_jobs": []}
            dump = json.dumps(jobs_list)
            f.write(dump)
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

    def _delete_job(self, sessionid, config):
        u"""job list から job を削除する"""
        jobs = self.jobs_list["oyakata_jobs"]
        for job in jobs:
            job_sessionid = job.keys()[0]
            job_name = job[job_sessionid].get('name', None)
            if job_sessionid == sessionid and config.name == job_name:
                print job
                jobs.remove(job)
                break
        self.jobs_list["oyakata_jobs"] = jobs
        jobs_path = self.config.jobs_file
        with open(jobs_path, "w") as f:
            try:
                f.seek(0)
                f.write(json.dumps(self.jobs_list))
                f.truncate()
            except IOError:
                print "nan...dato...!"

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

    @classmethod
    def from_dict(cls, config):
        d = config.copy()
        try:
            name = d.pop('name')
            cmd = d.pop('cmd')
        except KeyError:
            raise ValueError('invalid dict....')
        return cls(name, cmd, **d)

    def to_dict(self):
        d = dict(name=self.name, cmd=self.cmd)
        d.update(self.settings)
        return d

    def to_json(self):
        return json.dumps(self.to_dict())


class ProcessState(object):
    def __init__(self, config, sessionid, env=None):
        self.config = config
        self.sessionid = sessionid
        self.env = env
        self.running = deque()
        self.stop = False

        self.numprocess = int(config.settings.get("numprocess", 1))

    def make_process(self):
        cmd = self.config.cmd
        config_args = self.config.settings
        cmd_args = config_args.get("args", None)
        exc_cmd = [cmd, cmd_args]
        cwd = urllib.unquote(config_args.get("cwd"))
        return subprocess.Popen(exc_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, cwd=cwd)

    def update(self, config, env):
        self.config = config
        self.env = env
        self.numprocess = max(self.config.settings.get('numprocess', 1), self.numprocess)

    def queue(self, p):
        self.running.append(p)

    def dequeue(self, p):
        return self.running.popleft(p)

    def remove(self, p):
        try:
            self.running.remove(p)
        except ValueError:
            pass

    def list_process(self):
        return list(self.running)


