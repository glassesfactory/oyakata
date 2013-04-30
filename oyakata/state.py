#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
import heapq
from threading import RLock
import pyuv


class ProcessWatcher(object):
    u"""process watcher
    """

    def __init__(self, loop):
        self.processes = []
        self._timer = pyuv.Timer(loop)
        self._lock = RLock()

    def start(self, interval=0.1):
        self._timer.start(self._on_check, interval, interval)
        self._timer.unref()

    def stop(self):
        self.processes = []
        self._timer.stop()

    def close(self):
        self.processes = []

        if not self._timer.closed:
            self._timer.close()

    def check(self, p):
        heapq.heappush(self.processes, p)

    def _on_check(self):
        with self._lock:
            while True:
                if not len(self.processes):
                    #監視すべきプロセスが無くなった
                    break
                p = heapq.heappop(self.processes)
                if p.poll() is None:
                    heapq.heappush(self.processes, p)
                else:
                    try:
                        p.kill()
                    except:
                        raise


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
        # cmd = self.config.cmd
        # config_args = self.config.settings
        # cmd_args = config_args.get("args", None)
        # if not isinstance(cmd_args, list):
        #     cmd_args = [cmd_args]
        # exc_cmd = [cmd]
        # exc_cmd.extend(cmd_args)
        # cwd = urllib.unquote(config_args.get("cwd"))

        # shell = self.config.settings.get('shell', False)

        return self.config.make_process()
        # return subprocess.Popen(exc_cmd, stdout=subprocess.PIPE,
                                # stderr=subprocess.PIPE, shell=shell, cwd=cwd, env=self.env)

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

        :param p: add process
        """
        self.running.append(p)

    def dequeue(self, p):
        u"""popleft process from queue.
        キューの先頭からプロセスを削除し、そのプロセスを返します。

        :param p: dequeue process

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
