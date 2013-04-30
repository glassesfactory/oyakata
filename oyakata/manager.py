#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
from threading import RLock
import logging

import pyuv

from .error import ProcessError, ProcessConflict, ProcessNotFound
from .state import ProcessState, ProcessWatcher


class ProcessManager(object):
    u"""manage process.
    プロセスを管理します。

    :param config: manager config object.
    :param running_process: running process dict.

    """

    def __init__(self, loop=None):
        #default event loop.
        self.loop = loop or pyuv.Loop.default_loop()

        #u-n
        self._sessions = OrderedDict()
        self.processes = OrderedDict()
        self.running_process = OrderedDict()
        self._lock = RLock()
        self._watcher = ProcessWatcher(self.loop)
        self.started = False

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

        # self._save_job(sessionid, config)

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
        # self._delete_job(sessionid, config)

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
        # self._update_job(sessionid, config)

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

    def get_config(self, sessionid, name):
        if not sessionid in self._sessions:
            raise ProcessNotFound()

        try:
            state = self._sessions[sessionid][name]
        except KeyError:
            raise ProcessNotFound()

        return state.config

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
                # self._watcher.check(p)
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

    def start(self):
        self._watcher.start()
        self.started = True

    def stop(self):
        self._watcher.stop()
        self.loop.stop()
        self.started = False

    def run(self):
        if not self.started:
            return RuntimeError("Process Manager hasn't been started")
        self.loop.run()
