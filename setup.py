#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

py_version = sys.version_info[:2]

if py_version < (2, 7):
    raise RuntimeError('On Python 2, Oyakata requires Python 2.7 or better')

CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 2.7',
    'Topic :: System :: Boot',
    'Topic :: System :: Monitoring',
    'Topic :: System :: Systems Administration',
    'Topic :: Software Development :: Libraries']


setup(
    name='oyakata',
    version="0.1.0",
    description='simple system process manager',
    classifiers=CLASSIFIERS,
    license='MIT',
    author='Yamaguchi Eikichi',
    author_email='info@kageya.ma',
    packages=find_packages(),
    install_requires=[
      'docopt',
      'requests',
      'toml-python',
      'meinheld'
    ],
    entry_points="""
      [console_scripts]
      oyakatad=oyakata.oyakatad:run
      oyakata=oyakata.main:main
      """
    )
