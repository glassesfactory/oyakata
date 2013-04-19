#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, subprocess, select


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
    def __init__(self, proc, concurrencies, env, cwd):
        self.proc = proc
        self.concurrencies = concurrencies
        self.env = env
        self.cwd = cwd
        self.processes = []
        self.loggers = {}
        self.running = False
        self.loogers['system'] = _create_logger('system')

    def start_all(self):
        for id, cmd in self.proc:
            for i in xrange(int(self.concurrencies.get(id, 1))):
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=self.env, cwd=self.cwd)
                self.processes.append(p)
                self.loggers[p.pid] = logger = _create_logger('%s.%d' % (id, i + 1))
                logger.info('started with pid')

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


class ProcessConfig(object):
    def __init__(self, name, cmd, **settings):
        self.name = name
        self.cmd = cmd
        self.settings = settings

    def to_dict(self):
        d = dict(name=self.name, cmd=self.cmd)
        d.update(self.settings)
        return d

