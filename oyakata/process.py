#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib
import logging
import subprocess
from collections import OrderedDict, deque
from threading import RLock

from .error import ProcessError, ProcessConflict, ProcessNotFound


class ProcessManager(object):
    """
    manage process.
    """
    def __init__(self, config):
        self.config = config
        self._sessions = OrderedDict()
        self.processes = OrderedDict()
        self.running_process = OrderedDict()
        self.set_logging()
        self._lock = RLock()

        self._load_registerd_jobs()

    def load(self, config, sessionid):
        u"""load new application and add job to jobfile"""
        logging.info("load config")
        with self._lock:
            try:
                self._load_process(config, sessionid)
            except ProcessError:
                raise

        self._save_job(sessionid, config)
        return

    def unload(self, sessionid, name):
        u"""unload application and remove job from jobfile"""
        logging.info("unload config")
        if not sessionid in self._sessions:
            raise ProcessNotFound()

        state = self._sessions[sessionid][name]
        config = state.config
        with self._lock:
            try:
                self._unload_process(state, config, sessionid)
            except ProcessError:
                raise
        #remove job from jobfile
        self._delete_job(sessionid, config)

    def reload(self, config, sessionid):
        u"""reload process from updated config"""
        logging.info("reload config")
        #not found target application
        if not sessionid in self._sessions:
            raise ProcessNotFound()

        #has target application process
        #追加に鳴った場合どうすっかな
        try:
            state = self._sessions[sessionid][config.name]
        except KeyError:
            raise ProcessNotFound()

        with self._lock:
            try:
                self._reload_process(state, config, sessionid)
            except ProcessError:
                raise

        #update job file
        self._update_job(sessionid, config)

    def _load_process(self, config, sessionid):
        u"""processを読み込む"""
        if sessionid in self._sessions:
            raise ProcessConflict()
        else:
            self._sessions[sessionid] = OrderedDict()

        with self._lock:
            state = ProcessState(config, sessionid)
            self._sessions[sessionid][config.name] = state

        #job の開始
        self.start_job(state)

        #logging
        # self.loggers[p.pid] = logger = _create_logger('%s.%d' % (name, 1 + 1))
        # logger.info('started with pid')

    def _unload_process(self, state, config, sessionid):
        u"""process の unload"""
        try:
            self.stop_job(state)
        except:
            raise
        #lock するかなー
        self._sessions[sessionid].pop(config.name)
        try:
            del self._sessions[sessionid]
        except KeyError:
            pass

    def _reload_process(self, state, config, sessionid):
        u"""process を新しい設定からリロードする"""

        try:
            self.restart_job(state, config)
        except:
            logging.error("failed reload config: %s" % str(config.name))
            logging.info("config not reloaded")

            raise

        with self._lock:
            #新しい奴に入れ替え
            self._sessions[sessionid][config.name] = state

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
                    #state.running = group
                    break
                self.running_process.pop(p.pid)
                #logging kill process
                #logger["p.pid"].info("stop_process %s:%s" %(p.name, p.pid))
                p.kill()
        logging.info("stop process: %s" % state.config.name)

    def restart_job(self, state, config=None):
        u"""job を再起動する"""
        if not state.stop:
            self.stop_job(state)
        state.stop = False
        if config:
            state.update(config)
        state.reset()
        self.start_job(state)

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
        logging.info("start with pid: %s" % str(pid))

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
        u"""job を保存します"""
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
                logging.error("failed saving config: %s" % str(sessionid))
                logging.info("job file not saved")
                print "oh"

    def _delete_job(self, sessionid, config):
        u"""job list から job を削除する"""
        jobs = self.jobs_list["oyakata_jobs"]
        for job in jobs:
            job_sid = job.keys()[0]
            job_name = job[job_sid].get('name', None)
            if job_sid == sessionid and config.name == job_name:
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
                logging.error("failed delete config: %s" % str(sessionid))
                logging.info("job file not deleted")
                print "nan...dato...!"

    def _update_job(self, sessionid, config):
        u"""job list を更新する"""
        jobs = self.jobs_list["oyakata_jobs"]
        for job in jobs:
            job_sid = job.keys()[0]
            job_name = job[job_sid].get('name', None)
            if job_sid == sessionid and config.name == job_name:
                job[sessionid] = config.to_dict()
                break
        self.jobs_list["oyakata_jobs"] = jobs
        jobs_path = self.config.jobs_file
        with open(jobs_path, "w") as f:
            try:
                f.seek(0)
                f.write(json.dumps(self.jobs_list))
                f.truncate()
            except IOError:
                logging.error("failed update config: %s" % str(sessionid))
                logging.info("job file not updated")
                print "e..."

    def set_logging(self, level=None):
        logger = logging.getLogger()
        if self.config.back_log is not None:
            handler = logging.FileHandler(self.config.back_log)
        else:
            handler = logging.StreamHandler()
        if self.config.log_format == "ltsv":
            format = r"loglevel:%(levelname)s    time:[%(asctime)s]    process:[%(process)d]    body:[%(message)s]"
        else:
            format = r"%(asctime)s [%(process)d] [%(levelname)s] %(message)s"
        datefmt = r"%Y/%m/%d:%H:%M:%S"
        handler.setFormatter(logging.Formatter(format, datefmt))
        logger.addHandler(handler)
        if not level:
            level = logging.INFO
        logger.setLevel(level)


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
        if not isinstance(cmd_args, list):
            cmd_args = [cmd_args]
        #logging
        print "in make_process:: %s: %s" % (cmd, " ".join(cmd_args))
        exc_cmd = [cmd]
        exc_cmd.extend(cmd_args)
        cwd = urllib.unquote(config_args.get("cwd"))
        return subprocess.Popen(exc_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, cwd=cwd)

    def update(self, config, env=None):
        self.config = config
        self.env = env
        self.numprocess = int(max(self.config.settings.get('numprocess', 1), self.numprocess))

    def reset(self):
        self.numprocess = int(self.config.settings.get("numprocess", 1))

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

