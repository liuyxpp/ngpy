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
import datetime

from flaskext.wtf import Form,Required,Optional,NumberRange,Length
from flaskext.wtf import IntegerField,FloatField
from flaskext.wtf import SelectField,TextField,BooleanField
from flaskext.wtf import DateTimeField,TextAreaField

from .ngzodb import CHANGEABLE_SIM_PARAM, SIMULATION_STATUS

class SelectSimulationForm(Form):
    simulations = SelectField(u'Simulations') #,coerce=uuid.UUID)


class NewGroupForm(Form):
    name = TextField(u'Name',[Length(max=128)])
    batchvar = SelectField(u'Batch variable',choices=CHANGEABLE_SIM_PARAM)
    description = TextAreaField(u'Description',[Length(max=4096)])


class NewSimulationForm(Form):
    mode = BooleanField(u'Bactch mode')
    batchvar = SelectField(u'Batch variable',choices=CHANGEABLE_SIM_PARAM)
    batchmin = FloatField(u'Batch min')
    # set default value to pass validation
    batchstep = FloatField(u'Batch step',default=0)
    batchmax = FloatField(u'Batch max',default=0)
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
    interval_save = IntegerField(u'interval_save',[Required()])


class SearchSimulationForm(Form):
    name = TextField(u'Name')
    group = SelectField(u'Group')
    status = SelectField(u'Status',choices=SIMULATION_STATUS,default='all')

    set_lx = BooleanField(u'Set range for lx')
    from_lx = FloatField(u'The range of lx')
    to_lx = FloatField(u'To lx')

    set_Lx = BooleanField(u'Set range for Lx')
    from_Lx = FloatField(u'The range of Lx')
    to_Lx = FloatField(u'To Lx')

    set_dt = BooleanField(u'Set range for dt')
    from_dt = FloatField(u'The range of dt')
    to_dt = FloatField(u'To dt')

    set_max_t = BooleanField(u'Set range for max_t')
    from_max_t = FloatField(u'The range of max_t')
    to_max_t = FloatField(u'To max_t')

    set_k_MA = BooleanField(u'Set range for k_MA')
    from_k_MA = FloatField(u'The range of k_MA')
    to_k_MA = FloatField(u'To k_MA')

    set_nu_MA = BooleanField(u'Set range for nu_MA')
    from_nu_MA = FloatField(u'The range of nu_MA')
    to_nu_MA = FloatField(u'To nu_MA')

    set_k_SM = BooleanField(u'Set range for k_SM')
    from_k_SM = FloatField(u'The range of k_SM')
    to_k_SM = FloatField(u'To k_SM')

    set_nu_SM = BooleanField(u'Set range for nu_SM')
    from_nu_SM = FloatField(u'The range of nu_SM')
    to_nu_SM = FloatField(u'To nu_SM')

    set_n_SM = BooleanField(u'Set range for n_SM')
    from_n_SM = FloatField(u'The range of n_SM')
    to_n_SM = FloatField(u'To n_SM')

    set_r_seed = BooleanField(u'Set range for r_seed')
    from_r_seed = FloatField(u'The range of r_seed')
    to_r_seed = FloatField(u'To r_seed')

    set_r_test = BooleanField(u'Set range for r_test')
    from_r_test = FloatField(u'The range of r_test')
    to_r_test = FloatField(u'To r_test')

    set_create_time = BooleanField(
                u'Set range for create_time (format: %Y-%m-%d %H:%M:%S)')
    from_create_time = DateTimeField(u'The range of create_time')
    to_create_time = DateTimeField(u'To date')

    set_update_time = BooleanField(u'Set range for update_time')
    from_update_time = DateTimeField(u'The range of update_time')
    to_update_time = DateTimeField(u'To date')

    set_run_time = BooleanField(u'Set range for run_time')
    from_run_time = DateTimeField(u'The range of run_time')
    to_run_time = DateTimeField(u'To date')

    set_finish_time = BooleanField(u'Set range for finish_time')
    from_finish_time = DateTimeField(u'The range of finish_time')
    to_finish_time = DateTimeField(u'To date')

    set_abort_time = BooleanField(u'Set range for abort_time')
    from_abort_time = DateTimeField(u'The range of abort_time')
    to_abort_time = DateTimeField(u'To date')

