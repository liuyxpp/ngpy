#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    forms.py
    ~~~~~~~~

    froms.py is a python module which contains various WTForms.

    :copyright: (c) 2011 by Yi-Xin Liu (liuyxpp@gmail.com).
    :license: BSD, see LICENSE for more details.
"""

import uuid
from flaskext.wtf import Form,Required,Optional,NumberRange,Length
from flaskext.wtf import IntegerField,FloatField
from flaskext.wtf import SelectField,TextField,BooleanField

class SelectSimulationForm(Form):
    simulations = SelectField(u'Simulations') #,coerce=uuid.UUID)


class NewSimulationForm(Form):
    mode = BooleanField(u'Bactch mode')
    batchvar = SelectField(u'Batch variable',
                          choices=[('lx','lx'),('Lx','Lx'),('dt','dt'),
                                   ('max_t','max_t'),('k_MA','k_MA'),
                                   ('nu_MA','nu_MA'),('k_SM','k_SM'),
                                   ('nu_SM','nu_SM'),('n_SM','n_SM'),
                                   ('r_seed','r_seed'),('r_test','r_test')
                                  ])
    batchmin = FloatField(u'Batch min')
    batchstep = FloatField(u'Batch step')
    batchmax = FloatField(u'Batch max')
    name = TextField(u'Name',[Length(max=128)])
    group = SelectField(u'Group')
    lx = FloatField(u'lx',[Required(),NumberRange(1e3,1e6)])
    ly = FloatField(u'ly',[Required()])
    Lx = IntegerField(u'Lx',[Required(),NumberRange(1e2,1e4)])
    Ly = IntegerField(u'Ly',[Required()])
    dx = FloatField(u'dx',[Required()])
    dy = FloatField(u'dy',[Required()])
    Nx = FloatField(u'Nx',[Required()])
    dt = FloatField(u'dt',[Required(),NumberRange(1e-9,1)])
    max_t = FloatField(u'max_t',[Required(),NumberRange(1,1e6)])
    k_MA = FloatField(u'k_MA',[Required(),NumberRange(1e-9,1e9)])
    nu_MA = FloatField(u'nu_MA',[Required(),NumberRange(1e-9,1e9)])
    r0_SM = FloatField(u'r0_SM',[Required()])
    k_SM = FloatField(u'k_SM',[Required(),NumberRange(1e-9,1e9)])
    nu_SM = FloatField(u'nu_SM',[Required(),NumberRange(1e-9,1e9)])
    n_SM = FloatField(u'n_SM',[Required(),NumberRange(1e-9,1e9)])
    r_seed = FloatField(u'r_seed',[Required(),NumberRange(0,1e6)])
    r_test = FloatField(u'r_test',[Required(),NumberRange(0,1e6)])

