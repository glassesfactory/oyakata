#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
from flask import Flask

opt_str = ""

app = Flask(__name__)


@app.route('/')
def index():
    res = "test flask!\n" + opt_str
    return res


if __name__ == "__main__":
    parser = OptionParser()
    (options, args) = parser.parse_args()
    #nnn?
    opt_str = ",".join([str(i) for i in args])
    app.run()
