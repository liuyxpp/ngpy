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
from ConfigParser import SafeConfigParser
from persistent import Persistent

# ISO 8601. For recovering the datetime object from the datestring stored in
# ZODB database
ISO_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


class FormParam(Persistent):
    def __init__(self,form):
        self.lx = form.lx.data
        self.Lx = form.Lx.data
        #self.ly = form.ly.data
        #self.Ly = form.Ly.data
        self.ly = self.lx
        self.Ly = self.Lx
        #self.dx = form.dx.data
        #self.dy = form.dy.data
        self.dx = self.lx/self.Lx
        self.dy = self.dx
        self.dt = form.dt.data
        #self.Nx = form.Nx.data
        self.Nx = int(round(1/self.dt))
        self.max_t = form.max_t.data
        self.k_MA = form.k_MA.data
        self.nu_MA = form.nu_MA.data
        #self.r0_SM = form.r0_SM.data
        self.r0_SM = self.dx/2.0
        self.k_SM = form.k_SM.data
        self.nu_SM = form.nu_SM.data
        self.n_SM = form.n_SM.data
        self.r_seed = form.r_seed.data
        self.r_test = form.r_test.data
    def setval(self,attr,val):
        setattr(self,attr,val)
        # do extra relations
        if attr == 'lx':
            self.ly = self.lx
            self.dx = self.lx/self.Lx
            self.dy = self.dx
            self.r0_SM = self.dx/2.0
        if attr == 'Lx':
            self.Ly = self.Lx
            self.dx = self.lx/self.Lx
            self.dy = self.dx
            self.r0_SM = self.dx/2.0
        if attr == 'dt':
            self.Nx = int(round(1/self.dt))


class Group(object):
    def __init__(self,name="",batchvar="",sim_list="",description=""):
        self.name = name
        self.batchvar = batchvar
        self.simlist = sim_list
        self.description = description


class Parameters(object):
    def __init__(self,form=None):
        if form is not None:
            self.update_by_form(form)

    # initialize by FormParam
    def update_by_form(self,form):
        self.lx = form.lx
        self.Lx = form.Lx
        self.ly = form.lx
        self.Ly = form.Lx
        self.dx = form.dx
        self.dy = form.dy
        self.dt = form.dt
        self.Nx = form.Nx
        self.max_t = form.max_t
        self.k_MA = form.k_MA
        self.nu_MA = form.nu_MA
        self.r0_SM = form.r0_SM
        self.k_SM = form.k_SM
        self.nu_SM = form.nu_SM
        self.n_SM = form.n_SM
        self.r_seed = form.r_seed
        self.r_test = form.r_test


class GroupInfo(object):
    def __init__(self,group=None,param=None,inifile=None):
        if inifile is not None:
            self.read(inifile)
        elif group is not None and param is not None:
            self.group = group
            self.param = param
        else:
            self.group = Group()
            self.param = Parameters()

    def update(self,group=None,param=None):
        if group is not None:
            self.group = group
        if param is not None:
            self.param = param

    def read(self,inifile):
        ini = SafeConfigParser()
        # set this flag to make options case sensitive
        ini.optionxform = str
        ini.read(inifile)
        # [Group]
        self.group.name = ini.get('Group','name')
        self.group.batchvar = ini.get('Group','batchvar')
        self.group.simlist = ini.getfloat('Group','simlist')
        self.group.description = ini.get('Group','description')
        # [Param]
        self.param.lx = ini.getfloat('Param','lx')
        self.param.ly = ini.getfloat('Param','ly')
        self.param.dx = ini.getfloat('Param','dx')
        self.param.dy = ini.getfloat('Param','dy')
        self.param.Lx = ini.getint('Param','Lx')
        self.param.Ly = ini.getint('Param','Ly')
        self.param.dt = ini.getfloat('Param','dt')
        self.param.Nx = ini.getint('Param','Nx')
        self.param.max_t = ini.getfloat('Param','max_t')
        self.param.k_MA = ini.getfloat('Param','k_MA')
        self.param.nu_MA = ini.getfloat('Param','nu_MA')
        self.param.r0_SM = ini.getfloat('Param','r0_SM')
        self.param.k_SM = ini.getfloat('Param','k_SM')
        self.param.nu_SM = ini.getfloat('Param','nu_SM')
        self.param.n_SM = ini.getfloat('Param','n_SM')
        self.param.r_seed = ini.getfloat('Param','r_seed')
        self.param.r_test = ini.getfloat('Param','r_test')

    def write(self,inifile):
        ini = SafeConfigParser()
        # set this flag to make options case sensitive
        ini.optionxform = str
        # [Group]
        ini.add_section('Group')
        ini.set('Group','name',self.group.name)
        ini.set('Group','batchvar',self.group.batchvar)
        ini.set('Group','simlist',self.group.simlist)
        ini.set('Group','description',self.group.description)
        # [Param]
        ini.add_section('Param')
        ini.set('Param','lx',str(self.param.lx))
        ini.set('Param','ly',str(self.param.ly))
        ini.set('Param','dx',str(self.param.dx))
        ini.set('Param','dy',str(self.param.dy))
        ini.set('Param','Lx',str(self.param.Lx))
        ini.set('Param','Ly',str(self.param.Ly))
        ini.set('Param','dt',str(self.param.dt))
        ini.set('Param','Nx',str(self.param.Nx))
        ini.set('Param','max_t',str(self.param.max_t))
        ini.set('Param','k_MA',str(self.param.k_MA))
        ini.set('Param','nu_MA',str(self.param.nu_MA))
        ini.set('Param','r0_SM',str(self.param.r0_SM))
        ini.set('Param','k_SM',str(self.param.k_SM))
        ini.set('Param','nu_SM',str(self.param.nu_SM))
        ini.set('Param','n_SM',str(self.param.n_SM))
        ini.set('Param','r_seed',str(self.param.r_seed))
        ini.set('Param','r_test',str(self.param.r_test))
        # write file
        with open(inifile,'w') as f:
            ini.write(f)


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


