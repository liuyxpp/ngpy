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
from persistent import Persistent

# ISO 8601. For recovering the datetime object from the datestring stored in
# ZODB database
ISO_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


class FormParam(Persistent):
    def __init__(self,form):
        self.lx = form.lx.data
        self.Lx = form.Lx.data
        self.ly = form.ly.data
        self.Ly = form.Ly.data
        #self.ly = self.lx
        #self.Ly = self.Lx
        self.dx = form.dx.data
        self.dy = form.dy.data
        #self.dx = self.lx/self.Lx
        #self.dy = self.dx
        self.dt = form.dt.data
        self.Nx = form.Nx.data
        #self.Nx = int(round(1/self.dt))
        self.max_t = form.max_t.data
        self.k_MA = form.k_MA.data
        self.nu_MA = form.nu_MA.data
        self.r0_SM = form.r0_SM.data
        #self.r0_SM = self.dx/2.0
        self.k_SM = form.k_SM.data
        self.nu_SM = form.nu_SM.data
        self.n_SM = form.n_SM.data
        self.r_seed = form.r_seed.data
        self.r_test = form.r_test.data

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


