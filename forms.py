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
from flaskext.wtf import Form,Required,Optional,NumberRange
from flaskext.wtf import IntegerField,FloatField,SelectField

class SelectSimulationForm(Form):
    simulations = SelectField(u'Simulations') #,coerce=uuid.UUID)


class NewSimulationForm(Form):
    lx = FloatField(u'lx',[Required(),NumberRange(1e3,1e6)])
    Lx = IntegerField(u'Lx',[Required(),NumberRange(1e2,1e4)])
    dt = FloatField(u'dt',[Required(),NumberRange(1e-9,1)])
    max_t = FloatField(u'max_t',[Required(),NumberRange(1,1e6)])
    k_MA = FloatField(u'k_MA',[Required(),NumberRange(1e-9,1e9)])
    nu_MA = FloatField(u'nu_MA',[Required(),NumberRange(1e-9,1e9)])
    k_SM = FloatField(u'k_SM',[Required(),NumberRange(1e-9,1e9)])
    nu_SM = FloatField(u'nu_SM',[Required(),NumberRange(1e-9,1e9)])
    n_SM = FloatField(u'n_SM',[Required(),NumberRange(1e-9,1e9)])
    r_seed = FloatField(u'r_seed',[Required(),NumberRange(0,1e6)])
    r_test = FloatField(u'r_test',[Required(),NumberRange(0,1e6)])

