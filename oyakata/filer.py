#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import logging


class JobFileManager(object):
    #なまえ…
    u"""job file management
    """
    def __init__(self, config):
        self.config = config
        self.jobs_file = config.jobs_file

    def load_registered_job(self):
        #まだ jobs file がなかった時作ったほうがいい気がしてきた
        if not os.path.isfile(self.jobs_file):
            return
        #a-
        jobs_list = []
        with open(self.jobs_file) as f:
            data = f.read()
            if data == '':
                jobs_list = self._init_jobs_file()
                return
            else:
                jobs_list = json.loads(data)
        self.jobs_list = jobs_list
        return jobs_list

    def _init_jobs_file(self):
        u"""[private] initialize job file
        job file を作成する
        """
        try:
            with open(self.jobs_file, "r+") as f:
                jobs_list = {"oyakata_jobs": []}
                dump = json.dumps(jobs_list)
                f.write(dump)
        except IOError:
            raise
        return jobs_list

    def save_job(self, sessionid, config):
        u"""[private] save job to job file.
        job を保存します

        Args:
            sessionid: session id.
            config: configuration object that you want to save
        """
        job = {}
        job[sessionid] = config.to_dict()
        #add new job
        self.jobs_list["oyakata_jobs"].append(job)
        with open(self.jobs_file, "w") as f:
            try:
                f.seek(0)
                f.write(json.dumps(self.jobs_list))
                f.truncate()
            except IOError:
                logging.error("failed saving config: %s" % str(sessionid))
                logging.info("job file not saved")
        return self.jobs_list

    def delete_job(self, sessionid, config):
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

    def update_job(self, sessionid, config):
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
