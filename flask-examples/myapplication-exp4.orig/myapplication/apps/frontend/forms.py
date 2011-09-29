# -*- coding:utf-8 -*-

"""
    forms.py
    ~~~~~~~~
    Application forms used in admin.
    
    author: italo maia
    date: 30/07/2010
"""

from wtforms import Form, validators, \
    BooleanField, TextField, TextAreaField

class PageForm(Form):
    show_in_menu = BooleanField('Show in the navigation menu?')
    pagename = TextField('Page name', [validators.Length(min=4, max=100)])
    content = TextAreaField('Content')
