# -*- coding: utf-8 -*-
"""
    config.py
    ~~~~~~~~

    NGPy configurations

    :copyright: (c) 2011 by Yi-Xin Liu (liuyxpp@gmail.com).
    :license: BSD, see LICENSE for more details.
"""

class Dev(object):
    DEBUG = True
    SECRET_KEY = 'lyx'
    # The explicit hostname should be stated
    # instead of localhost for multiple nodes usage.
    ZODB_STORAGE = 'zeo://console:1234'
    REDIS_HOST = 'console'
    REDIS_QUEUE_KEY = 'simQ'


class Production(object):
    DEBUG = True
    SECRET_KEY = 'l887y882x0r824x822y'
    ZODB_STORAGE = 'zeo://c0109:1234'
    REDIS_HOST = 'c0109'
    REDIS_QUEUE_KEY = 'simQ'

