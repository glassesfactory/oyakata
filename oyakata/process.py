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
    u"""manage process.
    プロセスを管理します。

    :param config: manager config object.
    :param running_process: running process dict.

    """

    def __init__(self, config):
        self.config = config
        self.jobs_file = config.jobs_file
        self._sessions = OrderedDict()
        self.processes = OrderedDict()
        self.running_process = OrderedDict()
        self.set_logging()
        self._lock = RLock()

        self._load_registered_jobs()

    def load(self, config, sessionid):
        u"""load new application and add job to jobfile
        アプリケーションを追加し、ジョブファイルに追記します。

        :param config: load config object.
        :param sessionid:  session id.

        """
        logging.info("load config")
        with self._lock:
            try:
                self._load_process(config, sessionid)
            except ProcessError:
                raise

        self._save_job(sessionid, config)

    def unload(self, sessionid, name):
        u"""unload application and remove job from jobfile
        アプリケーションを停止し、ジョブリストからも削除します。

        :param sessionid: session id.
        :param name: unload process name.

        """
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
        u"""reload application from updated config
        新しいコンフィグを元にアプリケーションを再起動します。

        :param config: reload new config.
        :param sessionid: session id.

        """
        logging.info("reload config")
        #not found target application...
        if not sessionid in self._sessions:
            raise ProcessNotFound()

        #has target application process
        #追加になった場合どうすっかな
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

    def list(self):
        u"""list up registered application.
        現在登録されている job　一覧

        Returns:
            process list.
        """
        jobs = self._sessions
        job_str = ""
        for job in jobs:
            for k, v in jobs[job].iteritems():
                job_str += str(k) + " | "
                job_str += "running" if not v.stop else "stop"
                job_str += " | "
                job_str += str(v.numprocess)
                job_str += "\n"
        return job_str

    def _load_process(self, config, sessionid):
        u"""[private] load process.
        processを読み込む

        Args:
        :param config: config object.
        :param sessionid: session id.

        """
        if sessionid in self._sessions:
            raise ProcessConflict()
        else:
            self._sessions[sessionid] = OrderedDict()

        with self._lock:
            state = ProcessState(config, sessionid)
            self._sessions[sessionid][config.name] = state

        #start job
        #job の開始
        self.start_job(state)

    def _unload_process(self, state, config, sessionid):
        u"""[private] unload process.
        process の unload

        Args:
            state: process state object.
            config: process config object.
            sessionid: session id.
        """
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
        u"""[private] reload process form new config.
        process を新しい設定からリロードする

        Args:
            state: process state object.
            config: process config object.
            sessionid: session id.
        """
        try:
            self.restart_job(state, config)
        except:
            logging.error("failed reload config: %s" % str(config.name))
            logging.info("config not reloaded")

            raise

        with self._lock:
            #change new state obj
            #新しい奴に入れ替え
            self._sessions[sessionid][config.name] = state

    def start_job(self, state):
        u"""start job
        job を開始する

        :param state: process state object.
        """
        if state.stop:
            return
        if len(state.running) < state.numprocess:
            self._spawn_processes(state)

    def stop_job(self, state):
        u"""stop job
        job を停止する

        :param state: process state object.
        """
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
                p.kill()
        logging.info("stop process: %s" % state.config.name)

    def restart_job(self, state, config=None):
        u"""restart job.
        job を再起動する

        :param state: process state object.
        :param config: updated process config.
        """
        if not state.stop:
            self.stop_job(state)
        state.stop = False
        if config:
            state.update(config)
        state.reset()
        self.start_job(state)

    def _spawn_processes(self, state):
        u"""[private] spawn processes.
        指定された数で process を立ち上げる
        """
        num_to_start = state.numprocess - len(state.running)
        for i in range(num_to_start):
            self._spawn_process(state)

    def _spawn_process(self, state):
        u"""[private] spawn process.
        process を立ち上げる
        """
        p = state.make_process()
        state.queue(p)
        pid = p.pid
        self.running_process[pid] = p
        logging.info("start with pid: %s" % str(pid))

    def _load_registered_jobs(self):
        u"""[private] load registered jobs.
        job list に登録済みのprocessを立ち上げる
        """
        if not os.path.isfile(self.jobs_file):
            return
        with open(self.jobs_file) as f:
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

    def _init_jobs_file(self):
        u"""[private] initialize job file
        job file を作成する
        """
        with open(self.jobs_file, "r+") as f:
            jobs_list = {"oyakata_jobs": []}
            dump = json.dumps(jobs_list)
            f.write(dump)
        self.jobs_list = jobs_list

    def _save_job(self, sessionid, config):
        u"""[private] save job to job file.
        job を保存します

        Args:
            sessionid: session id.
            config: configuration object that you want to save
        """
        job = {}
        job[sessionid] = config.to_dict()
        self.jobs_list["oyakata_jobs"].append(job)
        with open(self.jobs_file, "w") as f:
            try:
                f.seek(0)
                f.write(json.dumps(self.jobs_list))
                f.truncate()
            except IOError:
                logging.error("failed saving config: %s" % str(sessionid))
                logging.info("job file not saved")
                print "oh"

    def _delete_job(self, sessionid, config):
        u"""[private] delete job from job file.
        job list から job を削除する

        Args:
            sessionid: session id.
            config: configuration object that you want to delete.
        """
        jobs = self.jobs_list["oyakata_jobs"]
        for job in jobs:
            job_sid = job.keys()[0]
            job_name = job[job_sid].get('name', None)
            if job_sid == sessionid and config.name == job_name:
                jobs.remove(job)
                break
        self.jobs_list["oyakata_jobs"] = jobs
        with open(self.jobs_file, "w") as f:
            try:
                f.seek(0)
                f.write(json.dumps(self.jobs_list))
                f.truncate()
            except IOError:
                logging.error("failed delete config: %s" % str(sessionid))
                logging.info("job file not deleted")
                print "nan...dato...!"

    def _update_job(self, sessionid, config):
        u"""[private] update job to job file.
        job list を更新する

        Args:
            sessionid: session id.
            config: configuration object that you want to update.
        """
        jobs = self.jobs_list["oyakata_jobs"]
        for job in jobs:
            job_sid = job.keys()[0]
            job_name = job[job_sid].get('name', None)
            if job_sid == sessionid and config.name == job_name:
                job[sessionid] = config.to_dict()
                break
        self.jobs_list["oyakata_jobs"] = jobs
        with open(self.jobs_file, "w") as f:
            try:
                f.seek(0)
                f.write(json.dumps(self.jobs_list))
                f.truncate()
            except IOError:
                logging.error("failed update config: %s" % str(sessionid))
                logging.info("job file not updated")
                print "e..."

    def set_logging(self, level=None):
        u"""set logging configuration.
        logging の設定をします。

        :param level:  default log level.
        """
        logger = logging.getLogger()
        if self.config.back_log is not None:
            handler = logging.FileHandler(self.config.back_log)
        else:
            handler = logging.StreamHandler()
        if self.config.log_format == "ltsv":
            format = r"""loglevel:%(levelname)s    time:[%(asctime)s]    process:[%(process)d]    body:[%(message)s]"""
        else:
            format = r"%(asctime)s [%(process)d] [%(levelname)s] %(message)s"
        datefmt = r"%Y/%m/%d:%H:%M:%S"
        handler.setFormatter(logging.Formatter(format, datefmt))
        logger.addHandler(handler)
        if not level:
            level = logging.INFO
        logger.setLevel(level)


import json


class ProcessConfig(object):
    u"""Process config object.
    プロセスの設定オブジェクト

    Attributes:
    :param name: process name.
    :param cmd: exec command.
    :param settings: process settings.

    """
    def __init__(self, name, cmd, **settings):
        self.name = name
        self.cmd = cmd
        self.settings = settings

    @classmethod
    def from_dict(cls, config):
        u"""create ProcessConfig instance from dict object.
        dict から ProcessConfig インスタンスを生成します。

        :param config: config dict

        """
        d = config.copy()
        try:
            name = d.pop('name')
            cmd = d.pop('cmd')
        except KeyError:
            raise ValueError('invalid dict....')
        return cls(name, cmd, **d)

    def to_dict(self):
        u"""convert to dict.
        dict に変換します。

        """
        d = dict(name=self.name, cmd=self.cmd)
        d.update(self.settings)
        return d

    def to_json(self):
        u"""convert to json.
        json に変換します。
        """
        return json.dumps(self.to_dict())


class ProcessState(object):
    u"""manage process state object.
    プロセスの状態を管理するオブジェクトです。

    :param config: session config
    :param sessionid: session id
    :param env: process environment.
    :param running: running process queue.
    :param stop: process to see if it is stopped
    :param numprocess: process num.
    """
    def __init__(self, config, sessionid, env=None):
        self.config = config
        self.sessionid = sessionid
        self.env = env
        self.running = deque()
        self.stop = False

        self.numprocess = int(config.settings.get("numprocess", 1))

    def make_process(self):
        u"""create new process.
        新しいプロセスを生成します。

        Returns:
            new subprocess.Popen object.
        """
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
        return subprocess.Popen(exc_cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=False, cwd=cwd)

    def update(self, config, env=None):
        u"""update process state form new config.
        新しいコンフィグから ProcessState オブジェクトを更新します。

        :param config: config object.
        :param env: process environment
        """
        self.config = config
        self.env = env
        self.numprocess = int(max(self.config.settings.get('numprocess', 1),
                              self.numprocess))

    def reset(self):
        u"""reset process state
        プロセスの状態を初期化します。
        """
        self.numprocess = int(self.config.settings.get("numprocess", 1))

    def queue(self, p):
        u"""add process
        プロセスをキューに追加します。

        Args:
            p: process
        """
        self.running.append(p)

    def dequeue(self, p):
        u"""popleft process from queue.
        キューの先頭からプロセスを削除し、そのプロセスを返します。

        :param p: process

        """
        p = None
        try:
            p = self.running.popleft(p)
        except IndexError:
            pass
        return p

    def remove(self, p):
        u"""remove process form queue.
        キューからプロセスを削除します。

        :param p: Process you want to delete

        """
        try:
            self.running.remove(p)
        except ValueError:
            pass

    def list_process(self):
        u"""running process
        動作中のプロセスをリストにして返します。
        """
        return list(self.running)
