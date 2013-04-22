#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ProcessError(Exception):
    def __init__(self, errno=400, reason="bad_request"):
        self.errno = errno
        self.reason = reason

    def __str__(self):
        return "%s: %s" % (self.errno, self.reason)


class ProcessConflict(ProcessError):
    def __init__(self, reason="process_conflict"):
        ProcessError.__init__(self, errno=409, reason=reason)
