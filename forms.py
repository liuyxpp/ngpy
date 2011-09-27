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
from flaskext.wtf import Form, SelectField, Required

class SelectSimulationForm(Form):
    simulations = SelectField(u'Simulations',coerce=uuid.UUID)

def test():
    pass

if __name__ == '__main__':
    test()


