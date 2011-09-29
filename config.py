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
    ZODB_STORAGE = 'zconfig:///export/home/lyx/opt/lyx/web/zeo-dev.conf'


class Production(object):
    DEBUG = True
    SECRET_KEY = 'l887y882x0r824x822y'
    ZODB_STORAGE = 'zconfig:///export/home/lyx/opt/lyx/web/zeo.conf'

