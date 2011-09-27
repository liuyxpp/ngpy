#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    ngutil.py
    ~~~~~~~~

    ngutil.py is a python module which contains utility functions and constants for ngpy project.

    :copyright: (c) 2011 by Yi-Xin Liu (liuyxpp@gmail.com).
    :license: BSD, see LICENSE for more details.
"""

import datetime

# ISO 8601. For recovering the datetime object from the datestring stored in
# ZODB database
ISO_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

def str2time(iso_datetime_str):
    return datetime.datetime.strptime(iso_datetime_str,ISO_TIME_FORMAT)


def now2str():
    return datetime.datetime.now().isoformat()


def test():
    nowstr = time2str()
    print nowstr
    now = str2time(nowstr)
    print now
    nowstr = time2str(now)
    print nowstr

if __name__ == '__main__':
    test()


